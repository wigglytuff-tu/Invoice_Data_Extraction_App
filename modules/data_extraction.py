# modules/data_extraction.py
import re
import logging
from assets.gst_state_codes import GST_STATE_CODES

PATTERNS = {
    'invoice_number': r'(?:invoice\s*#?:?\s*inv[\s-]*)(\d+)',
    'invoice_date': r'(?:Invoice Date|Date of Invoice|Date):?\s*([\d]{2} [A-Za-z]{3} [\d]{4})',
    'place_of_supply': r'Place of Supply:?\s*([A-Za-z0-9\s,-]+)',
    'taxable_value': r'Taxable Amount\s*₹?([\d,]+\.\d{2})',
    'final_amount': r'Total\s*₹?([\d,]+\.\d{2})'
}

def extract_gstin_numbers(text):
    """
    Extract supplier and recipient GSTINs from text.
    """
    gstin_pattern = r'GSTIN[\s:]*([0-9A-Z]{15})'
    gstin_matches = re.findall(gstin_pattern, text, re.IGNORECASE)
    gstin_supplier = 'Not Found'
    gstin_recipient = 'Not Found'
    if len(gstin_matches) >= 1:
        gstin_supplier = gstin_matches[0].upper()
    if len(gstin_matches) >= 2:
        gstin_recipient = gstin_matches[1].upper()
    return gstin_supplier, gstin_recipient

def extract_data_fields(text):
    """
    Extract data fields from text using regex patterns.
    """
    data = {}
    for field, pattern in PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[field] = match.group(1).replace(",", "").strip()
            logging.info(f"Extracted {field}: {data[field]}")
        else:
            data[field] = None
            logging.warning(f"Failed to extract {field}.")
    gstin_supplier, gstin_recipient = extract_gstin_numbers(text)
    data['gstin_supplier'] = gstin_supplier
    data['gstin_recipient'] = gstin_recipient
    return data

# Function to extract and store all CGST and SGST rates and amounts
def extract_and_calculate_rates_and_amounts(text):
    def extract_tax_details(pattern):
        matches = re.findall(pattern, text, re.IGNORECASE)
        rates = []
        amounts = []
        for rate, amount in matches:
            rate_value = float(rate.replace('%', '').strip())
            amount_value = float(amount.replace(',', '').strip())
            rates.append(rate_value)
            amounts.append(amount_value)
        return rates, amounts

    # Patterns for tax amounts
    cgst_pattern = r'CGST\s*([\d\.]+%)\s*₹?([\d,]+\.\d{2})'
    sgst_pattern = r'SGST\s*([\d\.]+%)\s*₹?([\d,]+\.\d{2})'
    igst_pattern = r'IGST\s*([\d\.]+%)\s*₹?([\d,]+\.\d{2})'

    # Extract tax details
    cgst_rates, cgst_amounts = extract_tax_details(cgst_pattern)
    sgst_rates, sgst_amounts = extract_tax_details(sgst_pattern)
    igst_rates, igst_amounts = extract_tax_details(igst_pattern)

    # Calculate total tax amounts
    total_cgst = sum(cgst_amounts)
    total_sgst = sum(sgst_amounts)
    total_igst = sum(igst_amounts)

    # Calculate total tax amount
    total_tax_amount = total_cgst + total_sgst + total_igst

    # Calculate weighted average rates
    def calculate_weighted_rate(rates, amounts):
        if amounts and sum(amounts) > 0:
            weighted_rate = sum(rate * amount for rate, amount in zip(rates, amounts)) / sum(amounts)
            return weighted_rate
        else:
            return 0

    weighted_cgst_rate = calculate_weighted_rate(cgst_rates, cgst_amounts)
    weighted_sgst_rate = calculate_weighted_rate(sgst_rates, sgst_amounts)
    weighted_igst_rate = calculate_weighted_rate(igst_rates, igst_amounts)

    return {
        'cgst_rates': cgst_rates,
        'cgst_amounts': cgst_amounts,
        'sgst_rates': sgst_rates,
        'sgst_amounts': sgst_amounts,
        'igst_rates': igst_rates,
        'igst_amounts': igst_amounts,
        'cgst_amount': total_cgst,
        'sgst_amount': total_sgst,
        'igst_amount': total_igst,
        'tax_amount': total_tax_amount,
        'weighted_cgst_rate': weighted_cgst_rate,
        'weighted_sgst_rate': weighted_sgst_rate,
        'weighted_igst_rate': weighted_igst_rate
    }

def get_place_of_origin(gstin_supplier):
    if gstin_supplier and gstin_supplier != 'Not Found':
        state_code = gstin_supplier[:2]
        place_of_origin = GST_STATE_CODES.get(state_code, "Unknown State")
        logging.info(f"Place of origin based on GSTIN {gstin_supplier}: {place_of_origin}")
        return state_code + '-' + place_of_origin
    return "Unknown State"
