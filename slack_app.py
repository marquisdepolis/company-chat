# slack_app.py:
import io
import pandas as pd
from pptx import Presentation
import docx
import PyPDF2
import tempfile
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


os.environ["SLACK_BOT_TOKEN"] = open_file('slack_bot_token.txt')
slack_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=slack_token)


def search_messages(query):
    try:
        response = client.search_messages(query=query)
        return response["messages"]["matches"]
    except SlackApiError as e:
        print(f"Error searching messages: {e}")
        return None


# ...
