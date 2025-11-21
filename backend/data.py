import boto3
import io
import tempfile
import os
import json
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader
import whisper

# --------- CONFIGURATION ---------
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
OUTPUT_KEY = os.getenv("OUTPUT_KEY")

# --------- SETUP CLIENTS & MODEL ---------
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)
model = whisper.load_model("base")

# --------- LIST & PROCESS ---------
response = s3.list_objects_v2(Bucket=BUCKET_NAME)
texts = []

for item in response.get("Contents", []):
    key = item["Key"]
    ext = os.path.splitext(key)[1].lower() 

    if ext not in (".pdf", ".png", ".jpg", ".jpeg", ".mp4", ".mov", ".avi", ".mkv"):
        continue

    data = s3.get_object(Bucket=BUCKET_NAME, Key=key)["Body"].read()

    if ext == ".pdf":
        pdf_stream = io.BytesIO(data)
        reader = PdfReader(pdf_stream)
        txt = "".join(page.extract_text() or "" for page in reader.pages)
        texts.append(txt)

    elif ext in (".png", ".jpg", ".jpeg"):
        img = Image.open(io.BytesIO(data))
        texts.append(pytesseract.image_to_string(img))

    elif ext in (".mp4", ".mov", ".avi", ".mkv"):
        with tempfile.NamedTemporaryFile(suffix=ext, delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            result = model.transcribe(tmp.name)
            texts.append(result["text"])


# --------- UPLOAD THE JSON BACK TO S3 ---------
payload = json.dumps(texts, ensure_ascii=False)

s3.put_object(
    Bucket=BUCKET_NAME,
    Key=OUTPUT_KEY,          
    Body=payload,
    ContentType="application/json",
)

print(f"✔️  Uploaded {len(texts)} documents as {OUTPUT_KEY}")
