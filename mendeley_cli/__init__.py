from pathlib import Path
import shutil
import logging
import os
import http
import http.server
import webbrowser
import base64
from urllib import parse
import json

from mendeley import Mendeley, MendeleyAuthorizationCodeAuthenticator
from mendeley.session import MendeleySession
from mendeley.auth import MendeleyAuthorizationCodeTokenRefresher
from mendeley.exception import MendeleyApiException, MendeleyException
import click
from tablib import formats, Dataset
from dotenv import load_dotenv


load_dotenv(Path('~').expanduser()/'.mendeley_cli'/'config')
load_dotenv(Path()/'.mendeley_cli'/'config')

logging.basicConfig(level=logging.ERROR)

tablib_formats = list(formats.registry._formats.keys())

mendeley_client = Mendeley(int(os.getenv('MENDELEY_CLIENT_ID')),
                           os.getenv('MENDELEY_CLIENT_SECRET'),
                           redirect_uri=os.getenv('MENDELEY_REDIRECT_URI'))
mendeley_token_b64 = os.getenv('MENDELEY_OAUTH2_TOKEN_BASE64', None)

callback_html = '''
<html>
<head>
  <title>Mendeley CLI</title>
</head>
<body>
Login succeeded. You can close this window or tab.<br />
Please follow messages in the terminal to save your token.
</body>
</html>
'''.encode()


class RH(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse.parse_qs(parse.urlparse(self.path).query)
        auth = mendeley_client.start_authorization_code_flow(query['state'][0])
        mendeley_session = auth.authenticate(f'{mendeley_client.redirect_uri}{self.path}')
        mendeley_token = json.dumps(mendeley_session.token)
        mendeley_token_b64 = base64.b64encode(mendeley_token.encode()).decode()
        self.send_response(http.HTTPStatus.OK)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(callback_html)
        print('Login succeeded.')
        print('Please set an environment variable MENDELEY_OAUTH2_TOKEN_BASE64 or add it to a config file:')
        print()
        print(f'MENDELEY_OAUTH2_TOKEN_BASE64={mendeley_token_b64}')
        print()


def get_session():
    if mendeley_token_b64 is None:
        raise MendeleyException('Login required. Please `mendeley get token` first.')
    else:
        mendeley_token = json.loads(base64.b64decode(mendeley_token_b64.encode()).decode())
        auth = MendeleyAuthorizationCodeAuthenticator(mendeley_client, None)
        mendeley_session = MendeleySession(auth.mendeley, token=mendeley_token, client=auth.client,
                                           refresher=MendeleyAuthorizationCodeTokenRefresher(auth))
    return mendeley_session


def get_documents(session, document_title=None, document_uuid=None, group_uuid=None):
    documents = session.documents
    if group_uuid is not None:
        documents.group_id = str(group_uuid)
    if document_title is None and document_uuid is None:
        return list(documents.iter())
    if document_uuid is None:
        return list(documents.advanced_search(title=document_title).iter())
    else:
        return [documents.get(document_uuid)]


def print_table(dataset: Dataset, print_format):
    fmt = print_format
    if fmt is None:
        fmt = 'cli'
    print(dataset.export(fmt, tablefmt='simple'))


@click.group(context_settings={'max_content_width': 120})
def cmd():
    """Required environemnt variables

    * MENDELEY_CLIENT_ID

    * MENDELEY_CLIENT_SECRET

    * MENDELEY_REDIRECT_URI

    * MENDELEY_OAUTH2_TOKEN_BASE64

    """
    pass


@cmd.group(name='get')
def cmd_get():
    pass


@cmd.group(name='attach')
def cmd_attach():
    pass


@cmd.group(name='delete')
def cmd_delete():
    pass


@cmd.group(name='create')
def cmd_create():
    pass


@cmd_get.command(name='token')
def cmd_get_token():
    """Login and get token"""
    webbrowser.open(mendeley_client.start_authorization_code_flow().get_login_url())
    netloc = parse.urlparse(mendeley_client.redirect_uri)
    http.server.HTTPServer((netloc.hostname, netloc.port), RH).handle_request()


@cmd_attach.command(name='file')
@click.option('--document-title', type=click.STRING, help='Document title')
@click.option('--document-uuid', type=click.UUID, help='Document UUID')
@click.option('--file', type=click.Path(exists=True), required=True, help='File path')
@click.option('--file-title', type=click.STRING, help='File name')
@click.option('--print-format', type=click.Choice(tablib_formats), help='Print format')
def cmd_attach_file(document_title, document_uuid, file, file_title, print_format):
    """Attach file"""
    session = get_session()
    documents = get_documents(session, document_title, document_uuid)
    assert len(documents) == 1, f'Found {len(documents)} documents.'
    document = documents[0]
    src_file = Path(file)
    dst_file = src_file
    if file_title is not None:
        dst_file = Path('/')/'tmp'/file_title
        shutil.copy(src_file, dst_file)
    try:
        document.attach_file(dst_file)
    except MendeleyApiException as e:
        if 'This file already exists for this document' in e.message:
            logging.warning(e.message)
        else:
            raise
    run_get_files(document_title, document_uuid, print_format, session)


@cmd_get.command(name='files')
@click.option('--document-title', type=click.STRING, help='Document title')
@click.option('--document-uuid', type=click.UUID, help='Document UUID')
@click.option('--print-format', type=click.Choice(tablib_formats), help='Print format')
def cmd_get_files(document_title, document_uuid, print_format):
    """List files"""
    session = get_session()
    run_get_files(document_title, document_uuid, print_format, session)


def run_get_files(document_title, document_uuid, print_format, session):
    documents = get_documents(session, document_title, document_uuid)
    dataset = Dataset(headers=['Document Title', 'File UUID', 'File Name', 'URL'])
    for document in documents:
        for file in document.files.list().items:
            dataset.append([
                document.title,
                file.id,
                file.file_name,
                f'https://www.mendeley.com/viewer/?fileId={file.id}&documentId={document.id}'
            ])
    print_table(dataset, print_format)


@cmd_delete.command(name='file')
@click.option('--document-title', type=click.STRING, help='Document title')
@click.option('--document-uuid', type=click.UUID, help='Document UUID')
@click.option('--file-uuid', type=click.UUID, required=True, help='File UUID')
@click.option('--print-format', type=click.Choice(tablib_formats), help='Print format')
def cmd_delete_file(document_title, document_uuid, file_uuid, print_format):
    """ Delete file"""
    session = get_session()
    documents = get_documents(session, document_title, document_uuid)
    assert len(documents) == 1, f'Found multiple documents for title "{document_title}" uuid {document_uuid}.'
    files = [_ for _ in documents[0].files.list().items if _.id == file_uuid]
    assert len(files) == 1, f'Found {len(files)} files for uuid {file_uuid}.'
    files[0].delete()
    run_get_files(document_title, document_uuid, print_format, session)


@cmd_get.command(name='documents')
@click.option('--document-title', type=click.STRING, help='Document title (e.g. --document-title "Paper One")')
@click.option('--document-uuid', type=click.UUID, help='Document UUID')
@click.option('--group-uuid', type=click.UUID, help='Group UUID')
@click.option('--print-format', type=click.Choice(tablib_formats+['bibtex']), help='Print format')
def cmd_get_documents(document_title, document_uuid, group_uuid, print_format):
    """List documents"""
    session = get_session()
    documents = get_documents(session, document_title, document_uuid, group_uuid)
    if print_format == 'bibtex':
        session.headers['Accept'] = "application/x-bibtex"
        for document in documents:
            print(session.get(f'/documents/{document.id}', params={'view': 'bib'}).text)
    else:
        dataset = Dataset(headers=['UUID', 'Title'])
        for document in documents:
            dataset.append([document.id, document.title])
        print_table(dataset, print_format)


@cmd_get.command(name='documenttypes')
@click.option('--print-format', type=click.Choice(tablib_formats), help='Print format')
def cmd_get_documenttypes(print_format):
    """Get available document types"""
    types = get_session().get('/document_types').json()
    dataset = Dataset(headers=['Name', 'Description'])
    for t in types:
        dataset.append([t['name'], t['description']])
    print_table(dataset, print_format)


@cmd_get.command(name='groups')
@click.option('--print-format', type=click.Choice(tablib_formats), help='Print format')
def cmd_get_groups(print_format):
    """Get groups"""
    groups = get_session().groups.list().items
    dataset = Dataset(headers=['UUID', 'Type', 'Name'])
    for group in groups:
        dataset.append([group.id, group.access_level, group.name])
    print_table(dataset, print_format)


@cmd_create.command(name='document')
@click.option('--title', type=click.STRING, required=True, help='Document title (e.g --title "Paper One")')
@click.option('--doctype', type=click.STRING, default='generic', show_default=True,
              help='Document type. Available document types are listed by `mendeley get documenttypes`.')
@click.option('--group-uuid', type=click.UUID, help='Group UUID')
@click.option('--hidden', type=click.BOOL, default=True, show_default=True, help='Exclude from Mendeley Catalog')
@click.option('--print-format', type=click.Choice(tablib_formats), help='Print format')
def cmd_create_document(title, doctype, group_uuid, hidden, print_format):
    """Create document"""
    session = get_session()
    documents = session.documents
    if group_uuid is not None:
        documents.group_id = str(group_uuid)
    document = documents.create(title, doctype, hidden=hidden)
    dataset = Dataset(headers=['UUID', 'Title'])
    dataset.append([document.id, document.title])
    print_table(dataset, print_format)


@cmd_delete.command(name='document')
@click.option('--document-uuid', type=click.UUID, required=True, help='Document UUID')
@click.option('--permanent', type=click.BOOL, default=False, show_default=True,
              help="Don't use trash. Delete it permanently.")
def cmd_delete_document(document_uuid, permanent):
    """Move document to trash or delete it permanently"""
    document = get_session().documents.get(document_uuid)
    if permanent:
        document.delete()
    else:
        document.move_to_trash()
