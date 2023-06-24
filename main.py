import fitz
import pytesseract
import re
import pandas as pd
from unidecode import unidecode
from io import BytesIO
from PIL import Image
import docx
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


def image_to_pdf(file_path):
    image = fitz.open(file_path)
    rect = image[0].rect
    # Create a new PDF document
    doc = fitz.open()

    pdfbytes = image.convert_to_pdf()
    imgPDF = fitz.open("pdf", pdfbytes)

    page = doc.new_page(width=rect.width, height=rect.height)
    page.show_pdf_page(rect, imgPDF, 0)

    # Save the PDF to the output file
    doc.save("output_pdf.pdf")
    doc.close()


def image_to_unstructured_text(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))

    doc = docx.Document()
    doc.add_paragraph(text)
    doc.save("newdoc.docx")

    return text


def if_image_is_pdf(file_path):
    pdf_file = file_path
    pdffile = fitz.open(file_path)

    images = convert_from_path(pdf_file)
    pdf_text = []
    for i in range(pdffile.page_count):

        text = pytesseract.image_to_string(images[i])

        data = pytesseract.image_to_data(images[i], output_type=pytesseract.Output.DICT)

        image_size = images[i].size

        page = pdffile[i]

        image_size_in_pdf = tuple(page.mediabox_size)

        data_details = []
        for text, i in zip(data['text'], range(len(data['text']))):
            if data['text'][i].strip() != '':
                line_num = data['line_num'][i]
                left_mar = data['left'][i]
                top_mar = data['top'][i]
                word_width = data['width'][i]
                word_hg = data['height'][i]

                data_details.append((line_num, left_mar, top_mar, word_width, word_hg, text))

        entries = []
        for g in data_details:
            # print("---------",g[5])
            pdf_text.append(g[5])
            x_start = g[1]
            y_start = g[2]

            font_size = round(g[4] / 100 * 60)

            if font_size > 14:
                font_size = 14

            if font_size < 9:
                font_size = 14

            #
            textbox_height = image_size[1]
            text = g[5]
            #
            text_width = image_size[0]
            entries.append((x_start, y_start, text_width, textbox_height, font_size, text))

        for writing in entries:
            # print(writing)

            x_text_in_image = writing[0]
            y_text_in_image = writing[1]

            x_text_in_pdf = (x_text_in_image / image_size[0]) * image_size_in_pdf[0]
            y_text_in_pdf = (y_text_in_image / image_size[1]) * image_size_in_pdf[1]

            text = writing[5]
            # print((x_text_in_pdf, y_text_in_pdf, writing[2], writing[3]))

            text_box = fitz.Rect(x_text_in_pdf + 0.5, y_text_in_pdf, writing[2], writing[3])

            # fontsize = writing[4]
            fontsize = 14
            # print(fontsize)
            color = (1, 0, 0)  # RGB values for red
            try:
                annot = page.insert_textbox(text_box, text, color=color, fontsize=fontsize)
            except Exception as e:
                print(e)
                pass

    pdffile.save('output.pdf')

    pdffile.close()


def image_to_text_pdf(image_path):
    # image_path = "page0.png"
    # image = fitz.open(image_path)
    # rect = image[0].rect
    image1 = Image.open(image_path)
    el = image1.convert('L')

    enh_img = el.filter(ImageFilter.DETAIL).filter(ImageFilter.EDGE_ENHANCE_MORE).filter(ImageFilter.SMOOTH_MORE)
    pil_image = enh_img.filter(ImageFilter.DETAIL)

    # enhancer = ImageEnhance.Contrast(pil_image2)
    # enhanced_image0 = enhancer.enhance(1.2)
    # enhancer1 = ImageEnhance.Brightness(pil_image2)
    # pil_image = enhancer1.enhance(1.1)

    # pil_image.show()
    pil_image.save("undone.pdf")
    # Create a new PDF document
    doc = fitz.open("undone.pdf")

    # pdfbytes = pil_image.convert_to_pdf()
    # imgPDF = fitz.open("pdf", pdfbytes)

    page = doc[0]
    image_size = pil_image.size
    # page = doc.new_page(width=image_size[0], height=image_size[1])
    # page.show_pdf_page(rect, imgPDF, 0)

    image_size_in_pdf = tuple(page.mediabox_size)
    print("image size: ", image_size)
    print("image in pdf: ", image_size_in_pdf)
    # Read the text from the images using pytesseract
    # text = pytesseract.image_to_string(image)
    data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
    # print(data)

    data_details = []
    for text, i in zip(data['text'], range(len(data['text']))):
        if data['text'][i].strip() != '':
            line_num = data['line_num'][i]
            left_mar = data['left'][i]
            top_mar = data['top'][i]
            word_width = data['width'][i]
            word_hg = data['height'][i]

            data_details.append((line_num, left_mar, top_mar, word_width, word_hg, text))

    entries = []

    for g in data_details:
        x_start = g[1]
        y_start = g[2]

        font_size = round(g[4])

        if font_size > 20:
            font_size = 20

        if font_size < 14:
            font_size = 14

        #
        textbox_height = image_size[1]
        text = g[5]
        #
        text_width = image_size[0]
        entries.append((x_start, y_start, text_width, textbox_height, font_size, text))

    for writing in entries:
        # print(writing)

        x_text_in_image = writing[0]
        y_text_in_image = writing[1]

        x_text_in_pdf = (x_text_in_image / image_size[0]) * image_size_in_pdf[0]
        y_text_in_pdf = (y_text_in_image / image_size[1]) * image_size_in_pdf[1]
        text = writing[5]
        # print((x_text_in_pdf, y_text_in_pdf, writing[2], writing[3]))

        text_box = fitz.Rect(x_text_in_pdf + 0.5, y_text_in_pdf - 0.5, writing[2], writing[3])
        fontsize = writing[4]
        color = (1, 0, 0)  # RGB values for red
        try:
            annot = page.insert_textbox(text_box, text, color=color,
                                        fontsize=fontsize)  # ,  stroke_opacity=0.5, fill_opacity=0.1)
        except Exception as e:
            print(e)
            print(writing)
            print(text_box)
            pass
    # Save the PDF to the output file
    doc.save("output_pdf.pdf")
    doc.close()