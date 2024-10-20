# modules/ocr.py
import cv2
import pytesseract
import numpy as np
import logging
import easyocr

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)

def preprocess_image(image):
    """
    Preprocess the image to improve OCR accuracy.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Apply thresholding to binarize the image
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Dilate and erode to remove noise
    kernel = np.ones((1, 1), np.uint8)
    processed_image = cv2.dilate(thresh, kernel, iterations=1)
    processed_image = cv2.erode(processed_image, kernel, iterations=1)
    return processed_image

def ocr_with_tesseract(image):
    """
    Perform OCR using Tesseract with confidence scoring.
    """
    try:
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        text = []
        confidences = []
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:
                text.append(data['text'][i])
                confidences.append(int(data['conf'][i]))
        full_text = ' '.join(text)
        average_confidence = sum(confidences) / len(confidences) if confidences else 0
        return full_text, average_confidence / 100
    except Exception as e:
        logging.error(f"Error during Tesseract OCR processing: {e}")
        return "", 0.0

def ocr_with_easyocr(image):
    """
    Perform OCR using EasyOCR with enhanced text assembly based on bounding boxes.
    """
    try:
        ocr_results = reader.readtext(image)
        extracted_text = []
        confidences = []
        prev_y = 0
        line_text = ""
        ocr_results_sorted = sorted(ocr_results, key=lambda x: x[0][0][1])
        for bbox, text, confidence in ocr_results_sorted:
            top_left_y = bbox[0][1]
            if abs(top_left_y - prev_y) < 30:
                line_text += " " + text
            else:
                if line_text:
                    extracted_text.append(line_text.strip())
                line_text = text
            prev_y = top_left_y
            confidences.append(confidence)
        if line_text:
            extracted_text.append(line_text.strip())
        full_text = "\n".join(extracted_text)
        average_confidence = sum(confidences) / len(confidences) if confidences else 0
        return full_text, average_confidence
    except Exception as e:
        logging.error(f"Error during EasyOCR processing: {e}")
        return "", 0.0
