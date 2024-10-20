# Invoice Data Extraction System

This project is an Invoice Data Extraction System designed to extract key information from invoices in PDF format. It leverages Optical Character Recognition (OCR) and natural language processing techniques to accurately extract data fields while ensuring trustworthiness and cost-effectiveness.

## Table of Contents

- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Technical Documentation](#technical-documentation)
  - [Approach and Algorithms](#approach-and-algorithms)
  - [Justification of Methods](#justification-of-methods)
  - [Trust Determination Method](#trust-determination-method)
- [Accuracy and Trust Assessment Report](#accuracy-and-trust-assessment-report)
  - [Accuracy of the System](#accuracy-of-the-system)
  - [Data Trustworthiness Analysis](#data-trustworthiness-analysis)
  - [Accuracy Check and Trust Determination Logic](#accuracy-check-and-trust-determination-logic)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

The Invoice Data Extraction System automates the process of extracting essential fields from invoice PDFs, such as invoice number, invoice date, GSTIN numbers, taxable value, tax amounts, and more. It supports both text-based and image-based PDFs, ensuring high accuracy and trustworthiness in the extracted data.

---
## Directory Structure
```
invoice_extraction_project/
├── app.py
├── main.py
├── requirements.txt
├── modules/
│   ├── __init__.py
│   ├── ocr.py
│   ├── data_extraction.py
│   ├── validation.py
│   └── utils.py
└── assets/
    └── gst_state_codes.py
```

- **app.py**: Streamlit application for the interactive UI.
- **main.py**: Main script integrating all modules.
- **requirements.txt**: Python package dependencies.
- **modules/**: Contains all Python modules, organized by functionality.
- **assets/**: Additional resources, such as GST state codes.

---

## Installation and Setup

### Prerequisites

- Python 3.6 or higher
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/invoice_extraction_project.git
   cd invoice_extraction_project
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**

   **Ubuntu/Debian**

   ```bash
   sudo apt-get install tesseract-ocr
   ```

   **Windows**

   Download and install from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).

4. **Run the Application**

   ```bash
   streamlit run app.py
   ```

   Access the application at [http://localhost:8501](http://localhost:8501).

## Usage

### Upload PDF Files
- Use the file uploader in the Streamlit app to select and upload one or more invoice PDFs.

### Processing and Extraction
- The system processes each PDF, displays the OCR confidence level, overall trust score, and any validation comments.

### Review Extracted Data
- Extracted data from all PDFs is displayed in a table within the app, allowing you to review the data.

### Download Results
- Choose to download the extracted data as a CSV or Excel file.

## Technical Documentation

### Approach and Algorithms

#### 1. PDF Classification
- **Objective**: Determine whether a PDF is text-based or image-based to decide the extraction method.
- **Method**:
  - Use **PyPDF2** to attempt text extraction from the first page.
  - If text is present, classify as text-based; otherwise, classify as image-based.

#### 2. Text Extraction
- **Text-Based PDFs**:
  - Use **pdfplumber** to extract text directly.
- **Image-Based PDFs**:
  - Convert PDF pages to images using **pdf2image**.
  - Preprocess images to enhance OCR accuracy:
    - Grayscale conversion.
    - Noise reduction using Gaussian blur.
    - Thresholding for binarization.
    - Dilation and erosion to remove noise.
  - Perform OCR using a tiered approach:
    - **First Attempt**: Use **Tesseract OCR**.
    - **Second Attempt**: If confidence is low, switch to **EasyOCR**.
  - Collect OCR confidence levels.

#### 3. Data Extraction
- **Regular Expressions (Regex)**:
  - Define patterns for fields like invoice number, invoice date, taxable value, etc.
  - Use regex to search and extract these fields from the preprocessed text.
- **GSTIN Extraction**:
  - Extract GSTINs using regex.
  - Assign the first GSTIN found to the supplier and the second to the recipient (if available).
- **Tax Details Extraction**:
  - Extract CGST, SGST, and IGST rates and amounts.
  - Store rates as lists to handle multiple tax rates.
  - Sum the amounts for each tax type.
- **Place of Origin Determination**:
  - Use the supplier's GSTIN to determine the state code and match it to the corresponding state.

#### 4. Data Validation
- **GSTIN Format Validation**:
  - Ensure extracted GSTINs match the standard format using regex.
- **Tax Applicability Checks**:
  - **CGST and SGST Presence**: Both should be present or both absent.
  - **Exclusivity of Taxes**: CGST/SGST and IGST should not be applied together.
  - **Allowed GST Rates**: Validate that extracted tax rates are among the allowed rates (e.g., 0%, 5%, 12%, 18%, 28%).
- **Place of Supply vs. Place of Origin**:
  - For intra-state transactions (same state code), only CGST and SGST should be applied.
  - For inter-state transactions (different state codes), only IGST should be applied.

#### 5. Trust Score Calculation
- **Field Validation Score**:
  - Calculate based on the number of validations passed.
- **Overall Trust Score**:
  - Dynamically computed as the average of OCR confidence level and field validation score.
  - Scale the score to a percentage (0-100%).

### Justification of Methods

- **Balance Between Cost-Effectiveness and Accuracy**:
  - **OCR Selection**:
    - **Tesseract OCR** is open-source and cost-effective but may have lower accuracy on complex images.
    - **EasyOCR** provides higher accuracy on challenging images and is also open-source. Based on SOTA deep learning method *CRAFT* using LSTMs.
    - The tiered approach uses Tesseract first and falls back to EasyOCR if necessary, optimizing cost and performance.
  - **Use of Regular Expressions**:
    - Regex provides a simple and efficient way to extract structured data from text.
    - Reduces the need for complex machine learning models, saving computational resources.
  - **Data Validation Logic**:
    - Implementing logical checks ensures data trustworthiness without significant computational overhead.
    - Focuses on domain-specific rules (e.g., GST regulations) to enhance accuracy.

### Trust Determination Method

To meet the requirement of determining data trustworthiness in **99% of cases**, the system:

- **Combines OCR Confidence with Field Validations**:
  - Ensures that both the text extraction process and the validity of the extracted data contribute to the trust score.
- **Implements Comprehensive Validation Checks**:
  - Validates critical fields that significantly impact trustworthiness.
  - Provides comments on any validation failures to highlight potential issues.
- **Calculates an Overall Trust Score**:
  - Provides a quantifiable measure of trustworthiness.
  - Enables users to make informed decisions based on the score.

## Accuracy and Trust Assessment Report

### Accuracy of the System
- The system is designed to achieve high accuracy through:
  - **Effective OCR Processing**:
    - Preprocessing images to enhance text recognition.
    - Using a tiered OCR approach to handle different types of PDFs.
  - **Structured Data Extraction**:
    - Utilizing regex patterns tailored to invoice formats.
    - Extracting GSTINs and tax details accurately.

### Data Trustworthiness Analysis
- **Validation of Critical Fields**:
  - Ensuring that essential fields like GSTIN, tax rates, and amounts are accurate.
- **Logical Consistency Checks**:
  - Verifying that the data adheres to GST laws and regulations.
- **Trust Score Implementation**:
  - Combining OCR confidence and validation results to provide a reliable trust score.

### Accuracy Check and Trust Determination Logic

#### 1. OCR Confidence Level
- **Text-Based PDFs**:
  - Assigned a confidence level of 100% due to direct text extraction.
- **Image-Based PDFs**:
  - OCR confidence level is calculated based on the OCR tool's confidence scores.

#### 2. Field Validation Score
- **Calculation**:
  - Number of validations passed divided by the total number of validations.
- **Validations Include**:
  - GSTIN format checks.
  - Tax rate validations.
  - Tax applicability based on transaction type.

#### 3. Overall Trust Score
- **Formula**:
  ```
  Overall Trust Score = ((OCR Confidence Level + Field Validation Score) / 2) * 100
  ```
- **Interpretation**:
  - A higher score indicates higher trustworthiness.
  - Scores close to 100% suggest that the data is accurate and reliable.

#### 4. Achieving 99% Trust Determination
- By implementing comprehensive validation checks and combining them with OCR confidence, the system can accurately determine the trustworthiness of the extracted data in the vast majority of cases.

**Error Handling and Comments**:
- Any validation failures are documented in the comments.
- Allows users to review and address specific issues.

# Invoice Extraction Project

## Directory Structure
```
invoice_extraction_project/
├── app.py
├── main.py
├── requirements.txt
├── modules/
│   ├── __init__.py
│   ├── ocr.py
│   ├── data_extraction.py
│   ├── validation.py
│   └── utils.py
└── assets/
    └── gst_state_codes.py
```

- **app.py**: Streamlit application for the interactive UI.
- **main.py**: Main script integrating all modules.
- **requirements.txt**: Python package dependencies.
- **modules/**: Contains all Python modules, organized by functionality.
- **assets/**: Additional resources, such as GST state codes.

---

## Installation and Setup

### Prerequisites

- Python 3.6 or higher
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/invoice_extraction_project.git
   cd invoice_extraction_project
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**

   **Ubuntu/Debian**

   ```bash
   sudo apt-get install tesseract-ocr
   ```

   **Windows**

   Download and install from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).

4. **Run the Application**

   ```bash
   streamlit run app.py
   ```

   Access the application at [http://localhost:8501](http://localhost:8501).

## Usage

### Upload PDF Files
- Use the file uploader in the Streamlit app to select and upload one or more invoice PDFs.

### Processing and Extraction
- The system processes each PDF, displays the OCR confidence level, overall trust score, and any validation comments.

### Review Extracted Data
- Extracted data from all PDFs is displayed in a table within the app, allowing you to review the data.

### Download Results
- Choose to download the extracted data as a CSV or Excel file.

## Technical Documentation

### Approach and Algorithms

#### 1. PDF Classification
- **Objective**: Determine whether a PDF is text-based or image-based to decide the extraction method.
- **Method**:
  - Use **PyPDF2** to attempt text extraction from the first page.
  - If text is present, classify as text-based; otherwise, classify as image-based.

#### 2. Text Extraction
- **Text-Based PDFs**:
  - Use **pdfplumber** to extract text directly.
- **Image-Based PDFs**:
  - Convert PDF pages to images using **pdf2image**.
  - Preprocess images to enhance OCR accuracy:
    - Grayscale conversion.
    - Noise reduction using Gaussian blur.
    - Thresholding for binarization.
    - Dilation and erosion to remove noise.
  - Perform OCR using a tiered approach:
    - **First Attempt**: Use **Tesseract OCR**.
    - **Second Attempt**: If confidence is low, switch to **EasyOCR**.
  - Collect OCR confidence levels.

#### 3. Data Extraction
- **Regular Expressions (Regex)**:
  - Define patterns for fields like invoice number, invoice date, taxable value, etc.
  - Use regex to search and extract these fields from the preprocessed text.
- **GSTIN Extraction**:
  - Extract GSTINs using regex.
  - Assign the first GSTIN found to the supplier and the second to the recipient (if available).
- **Tax Details Extraction**:
  - Extract CGST, SGST, and IGST rates and amounts.
  - Store rates as lists to handle multiple tax rates.
  - Sum the amounts for each tax type.
- **Place of Origin Determination**:
  - Use the supplier's GSTIN to determine the state code and match it to the corresponding state.

#### 4. Data Validation
- **GSTIN Format Validation**:
  - Ensure extracted GSTINs match the standard format using regex.
- **Tax Applicability Checks**:
  - **CGST and SGST Presence**: Both should be present or both absent.
  - **Exclusivity of Taxes**: CGST/SGST and IGST should not be applied together.
  - **Allowed GST Rates**: Validate that extracted tax rates are among the allowed rates (e.g., 0%, 5%, 12%, 18%, 28%).
- **Place of Supply vs. Place of Origin**:
  - For intra-state transactions (same state code), only CGST and SGST should be applied.
  - For inter-state transactions (different state codes), only IGST should be applied.

#### 5. Trust Score Calculation
- **Field Validation Score**:
  - Calculate based on the number of validations passed.
- **Overall Trust Score**:
  - Compute as the average of OCR confidence level and field validation score.
  - Scale the score to a percentage (0-100%).

### Justification of Methods

- **Balance Between Cost-Effectiveness and Accuracy**:
  - **OCR Selection**:
    - **Tesseract OCR** is open-source and cost-effective but may have lower accuracy on complex images.
    - **EasyOCR** provides higher accuracy on challenging images and is also open-source.
    - The tiered approach uses Tesseract first and falls back to EasyOCR if necessary, optimizing cost and performance.
  - **Use of Regular Expressions**:
    - Regex provides a simple and efficient way to extract structured data from text.
    - Reduces the need for complex machine learning models, saving computational resources.
  - **Data Validation Logic**:
    - Implementing logical checks ensures data trustworthiness without significant computational overhead.
    - Focuses on domain-specific rules (e.g., GST regulations) to enhance accuracy.

### Trust Determination Method

To meet the requirement of determining data trustworthiness in **99% of cases**, the system:

- **Combines OCR Confidence with Field Validations**:
  - Ensures that both the text extraction process and the validity of the extracted data contribute to the trust score.
- **Implements Comprehensive Validation Checks**:
  - Validates critical fields that significantly impact trustworthiness.
  - Provides comments on any validation failures to highlight potential issues.
- **Calculates an Overall Trust Score**:
  - Provides a quantifiable measure of trustworthiness.
  - Enables users to make informed decisions based on the score.

## Accuracy and Trust Assessment Report

### Accuracy of the System
- The system is designed to achieve high accuracy through:
  - **Effective OCR Processing**:
    - Preprocessing images to enhance text recognition.
    - Using a tiered OCR approach to handle different types of PDFs.
  - **Structured Data Extraction**:
    - Utilizing regex patterns tailored to invoice formats.
    - Extracting GSTINs and tax details accurately.

### Data Trustworthiness Analysis
- **Validation of Critical Fields**:
  - Ensuring that essential fields like GSTIN, tax rates, and amounts are accurate.
- **Logical Consistency Checks**:
  - Verifying that the data adheres to GST laws and regulations.
- **Trust Score Implementation**:
  - Combining OCR confidence and validation results to provide a reliable trust score.

### Accuracy Check and Trust Determination Logic

#### 1. OCR Confidence Level
- **Text-Based PDFs**:
  - Assigned a confidence level of 100% due to direct text extraction.
- **Image-Based PDFs**:
  - OCR confidence level is calculated based on the OCR tool's confidence scores.

#### 2. Field Validation Score
- **Calculation**:
  - Number of validations passed divided by the total number of validations.
- **Validations Include**:
  - GSTIN format checks.
  - Tax rate validations.
  - Tax applicability based on transaction type.

#### 3. Overall Trust Score
- **Formula**:
  ```
  Overall Trust Score = ((OCR Confidence Level + Field Validation Score) / 2) * 100
  ```
- **Interpretation**:
  - A higher score indicates higher trustworthiness.
  - Scores close to 100% suggest that the data is accurate and reliable.

#### 4. Achieving 99% Trust Determination
- By implementing comprehensive validation checks and combining them with OCR confidence, the system can accurately determine the trustworthiness of the extracted data in the vast majority of cases.

**Error Handling and Comments**:
- Any validation failures are documented in the comments.
- Allows users to review and address specific issues.

## Future System Approaches

### 1. Training NER's spaCy Transformers on Our Own Data
- **Objective**: Enhance entity extraction accuracy by training spaCy's Named Entity Recognition (NER) model on our own labeled invoice data.
- **Approach**: Collect a large number of invoice samples and annotate them with custom entity labels such as `invoice_number`, `invoice_date`, `tax_amount`, etc. Train a transformer-based model using spaCy's transformer pipeline to recognize these entities more accurately compared to a generic pre-trained model.

```python
import spacy
from spacy.tokens import DocBin

# Load a blank spaCy model
nlp = spacy.blank('en')

# Create and add a new NER pipeline
ner = nlp.add_pipe('ner')

# Define and add labels
LABELS = ['INVOICE_NUMBER', 'GSTIN', 'INVOICE_DATE', 'TAX_AMOUNT']
for label in LABELS:
    ner.add_label(label)

# Training process would involve loading annotated data and using it to update the model.
# Example code for the training pipeline would go here.
```

### 2. Using In-House Open Source LLMs like Mistral
- **Objective**: Improve data extraction accuracy without relying on third-party public LLMs for sensitive invoice data.
- **Approach**: Utilize an open-source, small LLM like **Mistral** hosted on in-house servers. This allows for fine-tuning with specific invoice data, enabling improved contextual understanding of different invoice formats while maintaining privacy and data security.
- **Justification**: Invoices often contain sensitive information that cannot be uploaded to public LLMs such as ChatGPT or Gemini. Using an in-house LLM ensures data privacy while benefiting from enhanced natural language understanding.

### 3. Improving OCR Accuracy Using Commercial OCRs
- **Objective**: Leverage advanced OCR solutions to further enhance extraction accuracy, particularly for poorly scanned invoices.
- **Approach**: Integrate commercial OCR services like **Google Vision**, **Amazon Textract**, or **Azure OCR** to improve text recognition accuracy. These OCR solutions use sophisticated algorithms and are capable of handling noisy, complex layouts more effectively than open-source solutions.
- **Integration Example**:
  ```python
  import boto3

  # Using Amazon Textract for OCR
  client = boto3.client('textract')
  with open('invoice.pdf', 'rb') as document:
      response = client.analyze_document(Document={'Bytes': document.read()}, FeatureTypes=['TABLES', 'FORMS'])

  # Process response to extract key information from the invoice
  # Example code for handling Textract response would go here.
  ```

