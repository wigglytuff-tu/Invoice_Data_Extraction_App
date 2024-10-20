# main.py
import os
import pandas as pd
import logging
from modules.utils import classify_pdf, extract_text_from_pdf, extract_text_from_image_pdf, preprocess_text
from modules.data_extraction import extract_data_fields, extract_and_calculate_rates_and_amounts, get_place_of_origin
from modules.validation import validate_fields, compute_overall_trust_score

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_pdf(file_path):
    """
    Process a single PDF file to extract invoice data.
    """
    print(f"\nProcessing file: {file_path}")
    pdf_type = classify_pdf(file_path)
    if pdf_type == 'text':
        raw_text = extract_text_from_pdf(file_path)
        ocr_confidence = 1.0  # 100% confidence for text-based PDFs
    else:
        raw_text, ocr_confidence = extract_text_from_image_pdf(file_path)
    print(f"OCR confidence level: {ocr_confidence * 100:.2f}%")
    if raw_text:
        preprocessed_text = preprocess_text(raw_text)
        extracted_data = extract_data_fields(preprocessed_text)
        tax_data = extract_and_calculate_rates_and_amounts(preprocessed_text)
        extracted_data.update(tax_data)
        extracted_data['place_of_origin'] = get_place_of_origin(extracted_data.get('gstin_supplier'))
        comments = validate_fields(extracted_data)
        overall_trust_score, comments = compute_overall_trust_score(extracted_data, ocr_confidence, comments)
        extracted_data['comments'] = '; '.join(comments) if comments else ''
        extracted_data['ocr_confidence'] = ocr_confidence * 100
        extracted_data['overall_trust_score'] = overall_trust_score
        print(f"Overall trust score for {file_path}: {overall_trust_score:.2f}%")
        return extracted_data
    else:
        return {}

def process_pdfs(file_paths):
    """
    Process multiple PDF files.
    """
    records = []
    for file_path in file_paths:
        data = process_pdf(file_path)
        records.append(data)
    return pd.DataFrame(records)

# The code to execute the processing would be in the UI part (see below)
