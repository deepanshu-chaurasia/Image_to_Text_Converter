from flask import Flask, send_file, render_template, request, redirect, url_for, send_from_directory, session
from main import image_to_unstructured_text, image_to_text_pdf
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
    file_path = f"data/{filename.replace('.', '_')}/{filename}"
    # image = Image.open(file_path)
    image = fitz.open(file_path)
    rect = image[0].rect
    # Create a new PDF document
    doc = fitz.open()

    pdfbytes = image.convert_to_pdf()
    imgPDF = fitz.open("pdf", pdfbytes)

    page = doc.new_page(width=rect.width, height=rect.height)
    page.show_pdf_page(rect, imgPDF, 0)

    temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.pdf')
    temp_filename = temp_file.name
    doc.save(temp_filename)

    return send_file(temp_filename)


@app.route('/read_image/<filename>')
def read_image(filename):
    file_path = f"./data/{filename.replace('.', '_')}/{filename}"
    pdf_path = f"C:/Users/deepa/PycharmProjects/Image_to_Text_Converter/data/{filename.replace('.', '_')}/{filename.replace('.', '_')}.pdf"

    text = image_to_unstructured_text(file_path)

    image_to_text_pdf(file_path, pdf_path)

    # return send_from_directory(f"data", filename)
    # files = [text, pdf_path]

    return render_template('image_reader.html', filename=filename, text=text, pdf_path=pdf_path)




if __name__ == '__main__':
    app.run(debug=True, port=8139)
