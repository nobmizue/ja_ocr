# ja_ocr
Japanese version OCR demo of Vision API

Make sure that Vision api in your GCP project is enabled.

1. create GCS bucket and modify the bucket name in app.yaml and also PROJECT_ID accordingly.
   PROJECT_ID = 'your GCP project id'
   CLOUD_STORAGE_BUCKET = 'new bucket name'

2. configure the proper acl to the GCS bucket.

3. pip install -r requirements.txt -t lib

4. gcloud app delopy
