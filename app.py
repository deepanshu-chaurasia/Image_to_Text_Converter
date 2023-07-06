from flask import Flask, send_file, render_template, request, redirect, url_for, send_from_directory, session
from main import image_to_unstructured_text
import tempfile
import threading
import csv
import os
import time
import fitz
import datetime
from unidecode import unidecode
from io import BytesIO
import pytesseract
from PIL import Image
import json
import logging

app = Flask(__name__)

#create logging system
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(message)s")


@app.route('/')
def index():
    image_file = request.args.get("image_file")
    return render_template('index.html', image_file=image_file)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = file.filename.replace(" ", "_")
    directory = f"./images/{filename.replace('.','_')}"
    os.makedirs(directory, exist_ok=True)
    file.save(os.path.join(directory, filename))
    return redirect(url_for('index', image_file = filename))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    file_path = f"images/{filename.replace('.','_')}/{filename}"
    # image = Image.open(file_path)
    image = fitz.open(file_path)
    # image_size = image.size
    # if image_size[0] > 720 or image_size[1] > 620:
    #     display_image = image.resize((round(image_size[0]/100*40), round(image_size[1]/100*40)))
    # else:
    #     display_image = image.resize((round(image_size[0]), round(image_size[1])))
    rect = image[0].rect
    # Create a new PDF document
    doc = fitz.open()

    # Add the image as a new page in the PDF

    # page = pdf[-1]  # Get the newly created page
    pdfbytes = image.convert_to_pdf()
    imgPDF = fitz.open("pdf", pdfbytes)

    page = doc.new_page(width=rect.width, height=rect.height)
    page.show_pdf_page(rect, imgPDF, 0)

    temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.pdf')
    temp_filename = temp_file.name
    doc.save(temp_filename)
    # return send_from_directory(f"images", filename)
    return send_file(temp_filename)


@app.route('/read_image/<filename>')
def read_image(filename):
    file_path = f"images/{filename.replace('.','_')}/{filename}"
    text = image_to_unstructured_text(file_path)

    return render_template('image_reader.html', filename=filename, text=text)

@app.route('/process_image/<filename>')
def process_image():
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=8139)
