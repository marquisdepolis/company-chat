from langchain.document_loaders import GoogleDriveLoader
from langchain.chains import VectorDBQA
from langchain.llms import OpenAI
import openai
import flask
import os
import urllib
import urllib.parse
import tkinter as tk
import google_drive
import slack_app
from tkinter import filedialog
from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
from datetime import datetime
from slack_sdk import WebClient
from database import init_db, insert_document, insert_message
from compliance_checker import check_compliance
from audit_logs import init_audit_logs_db, insert_audit_log

app = Flask(__name__)


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


directory = filedialog.askdirectory()
os.chdir(directory)
os.environ["OPENAI_API_KEY"] = open_file('openai_api_key.txt')
openai.api_key = open_file('openai_api_key.txt')
openai_api_key = openai.api_key

# Next, initialize the databases:
init_db()
init_audit_logs_db()
# Then, update the /chat route in your app.py:


@app.route('/')
def home():
    response = make_response(render_template('chat.html'))
    response.headers['Content-Type'] = 'text/html'
    return response


index = google_drive.build_index("SLC_Canon")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    # Check the compliance of the user input
    if not check_compliance(user_input):
        return jsonify({"error": "The input is not compliant"}), 400
    else:
        print("This text passes the compliance check.")
    # Call GPT-3.5 Turbo using the Chat API
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    model_response = response.choices[0].message.content

    # Save the conversation to audit logs
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insert_audit_log(user_input, model_response, timestamp)

    # Process the model's response for actions like searching Google Drive or Slack
    if "search Google Drive" in user_input:
        query = user_input.split("search Google Drive for ")[1]
        index.query_with_sources(query)

    if "search Slack" in user_input:
        query = user_input.split("search Slack for ")[1]
        # Might need to parse the query for url etc query = urllib.parse.quote(query)
        messages = search_messages(query)
        if messages:
            for message in messages:
                content = message["text"]
                timestamp = message["ts"]
                insert_message(content, timestamp)

    return jsonify(model_response)


if __name__ == "__main__":
    app.run(debug=True)
