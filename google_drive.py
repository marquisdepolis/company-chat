from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain.document_loaders import GoogleDriveLoader
from langchain.chains import VectorDBQA
from langchain.llms import OpenAI
import os
import faiss
import sqlite3
import numpy as np
import tempfile
import io
import PyPDF2
import docx
import pandas as pd
import pickle
from pptx import Presentation
from googleapiclient.errors import HttpError
import torch
from transformers import AutoTokenizer, AutoModel, BertTokenizer
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


def get_drive_service():
    key_file = 'google_oauth_account_key.json'
    scopes = ['https://www.googleapis.com/auth/drive']
    creds_file = 'token.pickle'
    creds = None

    # Load existing credentials if they exist
    if os.path.exists(creds_file):
        try:
            with open(creds_file, 'rb') as token:
                creds = pickle.load(token)
        except EOFError:
            # Handle the case when the token file is empty or corrupted
            creds = None

    # Check if the credentials are valid, and if not, request new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                key_file, scopes)
            creds = flow.run_local_server(port=0)
        # Save the new credentials
        with open(creds_file, 'wb') as token:
            pickle.dump(creds, token)
    try:
        service = build("drive", "v3", credentials=creds)
        print("success connecting to gdrive")
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


# Create a function to build the index and store it in SQLite:
def build_index(sqlite_filename):
    # Connect to SQLite database
    conn = sqlite3.connect(sqlite_filename)
    cur = conn.cursor()

    # Create the metadata table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY,
            file_id TEXT NOT NULL,
            file_name TEXT NOT NULL
        )
    """)
    conn.commit()

    # Get the Google Drive file list
    service = get_drive_service()
    results = service.files().list(q="mimeType != 'application/vnd.google-apps.folder'",
                                   fields="nextPageToken, files(id, name, mimeType)").execute()
    print("results are good", len(results))
    items = results.get("files", [])
    for item in items:
        file_id = item["id"]
        file_name = item["name"]
        print(file_name)
        file_mime_type = item["mimeType"]
        # Insert the metadata into the SQLite database
        cur.execute(
            "INSERT INTO metadata (file_id, file_name) VALUES (?, ?)", (file_id, file_name))
        conn.commit()

    # Close the SQLite connection
    conn.close()

    loader = GoogleDriveLoader(folder_id="0B8RtGaqgiPBcT1JJaXNjcUVNVDA")
    from langchain.indexes import VectorstoreIndexCreator
    index = VectorstoreIndexCreator().from_loaders([loader])
    return index
