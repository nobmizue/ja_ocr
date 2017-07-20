#!/usr/bin/env python

from flask import Flask, redirect, render_template, request, url_for
import requests
import logging
import os
import six
import base64
import datetime
from google.cloud import storage
from werkzeug import secure_filename

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

PROJECT_ID = "mizueproject"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
CLOUD_STORAGE_BUCKET = 'bucketdlp'

app = Flask(__name__)

#
# main 
#
@app.route('/')
def main():
        return render_template("list.html")

#
# Upload
#
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        data = request.form.to_dict(flat=True)
        image_url = upload_image_file(request.files.get('image'))

        ary = image_url.split("/")
        filename = ary[-1]
        gcsUrl = "gs://{0}/{1}".format(CLOUD_STORAGE_BUCKET, filename)

        if image_url:
            data['imageUrl'] = image_url

        data['text'] = detect_text(gcsUrl, 5)

        logging.debug("detected text:" + data['text'])

        return render_template("view.html", data=data)

    return render_template("form.html", action="Upload")

#
# Upload image file
#
def upload_image_file(file):

    if not file:
        return None

    logging.debug('start uploading:' + file.filename)

    filename = secure_filename(file.filename)
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
    basename, extension = filename.rsplit('.', 1)
    filename = "{0}-{1}.{2}".format(basename, date, extension)
    client = storage.Client(project=PROJECT_ID)

    bucket = client.bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(filename)
    blob.upload_from_string(
        file.read(),
        content_type=file.content_type)
    url = blob.public_url
    if isinstance(url, six.binary_type):
        url = url.decode('utf-8')

    logging.debug('uploaded:' + file.filename + " as " + url)

    return url

#
# Detect text
#
def detect_text(image_file, max_results=5):

    logging.debug("detect_text:" + image_file)

    access_token = "AIzaSyDYMsCVcXNrUxxW0JPSzJVE4WM0hfRfui4"
    url = 'https://vision.googleapis.com/v1/images:annotate?key={}'.format(access_token)
    header = {'Content-Type': 'application/json'}
    body = {
        'requests': [{
            'image': {
              'source': {
                'gcsImageUri':image_file
              },
            },
            'features': [{
                'type': 'TEXT_DETECTION',
                'maxResults': 3,
            }],
            'imageContext':{
                'languageHints':['ja']
            }

        }]
    }
    response = requests.post(url, headers=header, json=body).json()
    if len(response['responses']) <= 0:
        return ''

    text = []
    r = []

    text = response['responses'][0]['textAnnotations'][0]['description'] if len(response['responses'][0]) > 0 else ''

    return text
