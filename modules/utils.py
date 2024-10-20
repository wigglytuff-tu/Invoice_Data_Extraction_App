# modules/utils.py
import os
import re
import PyPDF2
import logging
from pdf2image import convert_from_path
from modules.ocr import preprocess_image, ocr_with_tesseract, ocr_with_easyocr

def classify_pdf(file_path):
    """
    Classify PDF as text-based or image-based.
    """
    print(f"Reading PDF file: {file_path}")
    try:
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            page = pdf_reader.pages[0]
            if page.extract_text().strip():
                print(f"Detected as text-based PDF.")
                return 'text'
            else:
                print(f"Detected as image-based PDF.")
                return 'image'
    except Exception as e:
        logging.error(f"Error classifying PDF: {e}")
        return 'image'

def extract_text_from_pdf(file_path):
    """
    Extract text from text-based PDF.
    """
    import pdfplumber
    print(f"Extracting text from text-based PDF: {file_path}")
    text = ''
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        logging.info(f"Extracted text from {file_path}.")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return ''

def extract_text_from_image_pdf(file_path):
    """
    Extract text from an image-based PDF using OCR.
    """
    print(f"Extracting text from image-based PDF: {file_path}")
    text = ''
    total_confidence = 0.0
    page_count = 0
    try:
        images = convert_from_path(file_path)
        for idx, image in enumerate(images):
            page_count += 1
            image = np.array(image)
            preprocessed_image = preprocess_image(image)
            print(f"Using Tesseract OCR for page {idx+1}")
            ocr_text_tess, confidence_tess = ocr_with_tesseract(preprocessed_image)
            logging.info(f"Tesseract OCR Confidence: {confidence_tess * 100:.2f}%")
            if confidence_tess >= 0.8:
                text += ocr_text_tess + "\n"
                total_confidence += confidence_tess
                continue
            else:
                print(f"Tesseract OCR confidence too low ({confidence_tess * 100:.2f}%), switching to EasyOCR for page {idx+1}")
                ocr_text_easy, confidence_easy = ocr_with_easyocr(preprocessed_image)
                logging.info(f"EasyOCR Confidence: {confidence_easy * 100:.2f}%")
                if confidence_easy >= 0.8:
                    text += ocr_text_easy + "\n"
                    total_confidence += confidence_easy
                    continue
                else:
                    logging.warning(f"OCR failed for page {idx + 1} of {file_path}.")
                    total_confidence += 0
        if page_count > 0:
            avg_confidence = total_confidence / page_count
        else:
            avg_confidence = 0.0
        logging.info(f"Successfully extracted text from {file_path}.")
        return text, avg_confidence
    except Exception as e:
        logging.error(f"Error extracting text from image PDF: {e}")
        return '', 0.0

def preprocess_text(text):
    """
    Preprocess text for data extraction.
    """
    text = re.sub(r'\s+', ' ', text)
    text = text.lower()
    logging.info("Preprocessed text.")
    return text
