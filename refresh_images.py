from __future__ import print_function
import httplib2
import os
import time

from apiclient import discovery
from apiclient import errors
from apiclient import http
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

ROTATION_SIZE = 3
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
IMAGES_DIR = 'images'
N_IMAGES = 20


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = '.'
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'creds.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def list_images():
	path = IMAGES_DIR
	name_list = os.listdir(path)
	full_list = [os.path.join(path,i) for i in name_list]
	time_sorted_list = sorted(full_list, key=os.path.getmtime)

	return time_sorted_list

def main():
    try:
        DONNA_FOLDER = open('donna_folder.id').readline().rstrip()
    except IOError as e:
        print('Could not find donna folder id')
        exit(1)

    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)

    results = service.children().list(folderId=DONNA_FOLDER, orderBy='modifiedDate desc', maxResults=N_IMAGES).execute()
    #download = download_file(service, '1OjZ0i1Qnk1Kwwc-OyTMNO3GSuNGF_G54dw', fd)
    items = results.get('items', [])
    if not items:
        print('No files found.')
    else:
        print('Files to download:')
        for item in items:
            id = item['id']
            file_location = IMAGES_DIR + '/' + id
            tmp_file_location = '/tmp/' + id + str(time.time())

            if not os.path.isfile(file_location):
                tfd = open(tmp_file_location, 'wb')
                download_file(service, id, tfd)
                os.rename(tmp_file_location, file_location)

     # keep only the last N_IMAGES
    images = list_images()
    if len(images) > N_IMAGES:
        for image in images[N_IMAGES:]:
            os.unlink(image)
            print("Removed {0}".format(image))


def download_file(service, file_id, local_fd):
    """Download a Drive file's content to the local filesystem.

     Args:
    service: Drive API Service instance.
    file_id: ID of the Drive file that will downloaded.
    local_fd: io.Base or file object, the stream that the Drive file's
        contents will be written to.
    """
    file = service.files().get(fileId=file_id).execute()

    if (file['mimeType'] == 'video/mp4'):
        return

    request = service.files().get_media(fileId=file_id)
    media_request = http.MediaIoBaseDownload(local_fd, request)

    while True:
        try:
            download_progress, done = media_request.next_chunk()
        except errors.HttpError, error:
            print('An error occurred: {0}'.format(error))
            return
        if download_progress:
            print('Download Progress: {0}%'.format(int(download_progress.progress() * 100)))
        if done:
            print('Download Complete')
            return

if __name__ == '__main__':
    main()
