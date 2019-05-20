from pathlib import Path
import shutil
import logging
import os

import requests
from mendeley import Mendeley
from mendeley.exception import MendeleyApiException
import click
from tablib import Dataset
from dotenv import load_dotenv


load_dotenv(Path('~').expanduser()/'.mendeley_cli'/'config')
load_dotenv(Path()/'.mendeley_cli'/'config')


def get_session():
    auth = Mendeley(int(os.getenv('MENDELEY_CLIENT_ID')),
                    redirect_uri=os.getenv('MENDELEY_REDIRECT_URI')).start_implicit_grant_flow()
    res = requests.post(auth.get_login_url(), allow_redirects=False,
                        data={'username': os.getenv('MENDELEY_USERNAME'), 'password': os.getenv('MENDELEY_PASSWORD')})
    return auth.authenticate(res.headers['Location'])


def get_documents(session, document_title=None, document_uuid=None):
    if document_uuid is not None:
        documents = [session.documents.get(document_uuid)]
    else:
        documents = session.documents.advanced_search(title=document_title).list().items
    return documents


def print_table(dataset: Dataset, print_format):
    if print_format == 'json':
        print(dataset.json)
    else:
        print(dataset)


@click.group()
def cmd():
    """Required environemnt variables

    * MENDELEY_USERNAME

    * MENDELEY_PASSWORD

    * MENDELEY_CLIENT_ID

    * MENDELEY_REDIRECT_URI
    """
    pass


@cmd.group(name='list')
def cmd_list():
    pass


@cmd.group(name='attach')
def cmd_attach():
    pass


@cmd.group(name='delete')
def cmd_delete():
    pass


@cmd_attach.command(name='file')
@click.option('--document-title', type=str, help='Document title')
@click.option('--document-uuid', type=str, help='Document UUID')
@click.option('--file', type=click.Path(exists=True), required=True, help='File path')
@click.option('--file-title', type=str, help='File name')
@click.option('--print-format', type=click.Choice(['table', 'json']), default='table', help='Print format')
def cmd_attach_file(document_title, document_uuid, file, file_title, print_format):
    """Attach file
    """
    session = get_session()
    documents = get_documents(session, document_title, document_uuid)
    assert len(documents) == 1, f'Found multiple documents.'
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
    run_list_files(document_title, document_uuid, print_format, session)


@cmd_list.command(name='files')
@click.option('--document-title', type=str, help='Document title')
@click.option('--document-uuid', type=str, help='Document UUID')
@click.option('--print-format', type=click.Choice(['table', 'json']), default='table', help='Print format')
def cmd_list_files(document_title, document_uuid, print_format):
    """List files
    """
    session = get_session()
    run_list_files(document_title, document_uuid, print_format, session)


def run_list_files(document_title, document_uuid, print_format, session):
    documents = get_documents(session, document_title, document_uuid)
    dataset = Dataset(headers=['Document', 'UUID', 'Name'])
    for document in documents:
        for file in document.files.list().items:
            dataset.append([
                document.title,
                file.id,
                file.file_name
            ])
    print_table(dataset, print_format=print_format)


@cmd_delete.command(name='file')
@click.option('--document-title', type=str, help='Document title')
@click.option('--document-uuid', type=str, help='Document UUID')
@click.option('--file-uuid', type=str, required=True, help='File UUID')
@click.option('--print-format', type=click.Choice(['table', 'json']), default='table', help='Print format')
def cmd_delete_file(document_title, document_uuid, file_uuid, print_format):
    """ Delete file
    """
    session = get_session()
    documents = get_documents(session, document_title, document_uuid)
    assert len(documents) == 1, f'Found multiple documents for title {document_title} uuid {document_uuid}.'
    files = [_ for _ in documents[0].files.list().items if _.id == file_uuid]
    assert len(files) == 1, f'Found {len(files)} files for uuid {file_uuid}.'
    files[0].delete()
    run_list_files(document_title, document_uuid, print_format, session)


@cmd_list.command(name='documents')
@click.option('--document-title', type=str, required=True, help='Document title')
@click.option('--print-format', type=click.Choice(['table', 'json']), default='table', help='Print format')
def cmd_list_docuemnts(document_title, print_format):
    """List documents"""
    session = get_session()
    documents = get_documents(session, document_title)
    dataset = Dataset(headers=['UUID', 'Title', 'Created'])
    for document in documents:
        dataset.append([
            document.id,
            document.title,
            document.created
        ])
    print_table(dataset, print_format=print_format)
