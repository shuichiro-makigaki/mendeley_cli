from pathlib import Path
from datetime import datetime
import shutil
import logging
import os

import requests
from mendeley import Mendeley
from mendeley.exception import MendeleyApiException
import click
from tablib import Dataset


def get_session(client_id, redirect_uri, username, password):
    auth = Mendeley(client_id, redirect_uri=redirect_uri).start_implicit_grant_flow()
    res = requests.post(auth.get_login_url(), allow_redirects=False,
                        data={'username': username, 'password': password})
    return auth.authenticate(res.headers['Location'])


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


@cmd.group(name='document')
def cmd_document():
    pass


@cmd.group(name='file')
def cmd_file():
    pass


@cmd_file.command(name='attach')
@click.option('--document-title', type=str, required=True, help='Document title')
@click.option('--document-uuid', type=str, help='Document UUID')
@click.option('--file', type=str, required=True, help='File path')
def attach_file(document_title: str, file: str):
    """Attach file to document
    """
    session = get_session(int(os.getenv('MENDELEY_CLIENT_ID')),
                          os.getenv('MENDELEY_REDIRECT_URI'),
                          os.getenv('MENDELEY_USERNAME'),
                          os.getenv('MENDELEY_PASSWORD'))
    document = session.documents.advanced_search(title=document_title).list().items
    assert len(document) == 1, f'Found multiple documents.'
    document = document[0]
    timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')
    src_file = Path(file)
    dst_file = Path(f'/tmp/{src_file.stem}_{timestamp}.{src_file.suffix}')
    shutil.copy(src_file, dst_file)
    try:
        document.attach_file(dst_file)
    except MendeleyApiException as e:
        if 'This file already exists for this document' in e.message:
            logging.warning(e.message)
        else:
            raise


@cmd_file.command(name='list')
@click.option('--document-title', type=str, required=True, help='Document title')
@click.option('--document-uuid', type=str, help='Document UUID')
def list_files(document_title: str):
    """List files
    """
    session = get_session(int(os.getenv('MENDELEY_CLIENT_ID')),
                          os.getenv('MENDELEY_REDIRECT_URI'),
                          os.getenv('MENDELEY_USERNAME'),
                          os.getenv('MENDELEY_PASSWORD'))
    documents = session.documents.advanced_search(title=document_title).list().items
    for document in documents:
        for file in document.files.list().items:
            print(file.id)
            print(file.file_name)
            print(file.size)
            print(file.mime_type)


@cmd_file.command(name='delete')
@click.option('--document-title', type=str, required=True, help='Document title')
@click.option('--file-uuid', type=str, required=True, help='File UUID')
@click.option('--document-uuid', type=str, help='Document UUID')
def delete_file(document_title: str, file_uuid: str):
    """ Delete file
    """
    session = get_session(int(os.getenv('MENDELEY_CLIENT_ID')),
                          os.getenv('MENDELEY_REDIRECT_URI'),
                          os.getenv('MENDELEY_USERNAME'),
                          os.getenv('MENDELEY_PASSWORD'))
    documents = session.documents.advanced_search(title=document_title).list().items
    assert len(documents) == 1, f'Found multiple documents for title {document_title}.'
    document = documents[0]
    files = [_ for _ in document.files.list().items if _.id == file_uuid]
    assert len(files) == 1, f'Found {len(files)} files for UUID {file_uuid}.'
    files[0].delete()


@cmd_document.command(name='list')
@click.option('--title', type=str, required=True, help='Document title')
@click.option('--format', type=str, default='table', help='table, json')
def list_docuemnts(title: str, format: str):
    """List documents"""
    session = get_session(int(os.getenv('MENDELEY_CLIENT_ID')),
                          os.getenv('MENDELEY_REDIRECT_URI'),
                          os.getenv('MENDELEY_USERNAME'),
                          os.getenv('MENDELEY_PASSWORD'))
    documents = session.documents.advanced_search(title=title).list().items
    dataset = Dataset(headers=['UUID', 'Title', 'Created'])
    for document in documents:
        dataset.append([
            document.id,
            document.title,
            document.created
        ])
    print_table(dataset, print_format=format)
