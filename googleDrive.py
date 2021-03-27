import pickle
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
import datetime
from datetime import datetime
import time

def Create_Service(client_secret_file, api_name, api_version, *scopes):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        return service
    except Exception as e:
        print('Unable to connect.')
        return None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt

def uploadFile():
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service('credentials.json',API_NAME,API_VERSION,SCOPES)
    folderID = '19QrYgTBw3S3s2Qypqb6WaUtfDagA0QLY'
    mime_type = 'application/x-sqlite3'
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    file_name = dt_string + '.db'

    file_metadata = {
        'name' : file_name,
        'parents': [folderID],
    }
    upload = MediaFileUpload('test.db',mimetype=mime_type)
    service.files().create(body=file_metadata,media_body=upload,fields='id').execute()

def upload():
    while True:
        print("Backup Alindi")
        uploadFile()
        time.sleep(21600)
