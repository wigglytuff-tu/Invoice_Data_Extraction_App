
# Function to validate fields
def validate_fields(extracted_data):
    """
    Validate individual fields and return validation results.
    """
    validation_results = []
    comments = []
    
     # Check that both CGST and SGST are present or both absent
    cgst_amount = extracted_data.get('cgst_amount', 0)
    sgst_amount = extracted_data.get('sgst_amount', 0)
    igst_amount = extracted_data.get('igst_amount', 0)

    if (cgst_amount > 0 and sgst_amount == 0) or (cgst_amount == 0 and sgst_amount > 0):
        comments.append('CGST and SGST should both be present or both absent')

    # Check that CGST+SGST and IGST are exclusive
    if (cgst_amount > 0 or sgst_amount > 0) and igst_amount > 0:
        comments.append('CGST/SGST and IGST should not be present together')

    # Validate that CGST and SGST rates are allowed
    allowed_gst_rates = [0, 2.5, 5, 6, 9, 12, 14, 18, 28]

    # Validate CGST rates
    for rate in extracted_data.get('cgst_rates', []):
        if rate not in allowed_gst_rates:
            comments.append(f'Invalid CGST Rate: {rate}')
            break

    # Validate SGST rates
    for rate in extracted_data.get('sgst_rates', []):
        if rate not in allowed_gst_rates:
            comments.append(f'Invalid SGST Rate: {rate}')
            break

    # Validate IGST rates
    for rate in extracted_data.get('igst_rates', []):
        if rate not in allowed_gst_rates:
            comments.append(f'Invalid IGST Rate: {rate}')
            break

    # Check tax applicability based on place of supply and origin
    place_of_supply = extracted_data.get('place_of_supply', '')
    place_of_origin = extracted_data.get('place_of_origin', '')

    if place_of_supply and place_of_origin:
        pos_state_code = place_of_supply[:2]
        poo_state_code = place_of_origin[:2]
        if pos_state_code == poo_state_code:
            # Should have CGST and SGST
            if extracted_data.get('igst_amount', 0) > 0:
                comments.append('IGST should not be applied for intra-state transactions')
        else:
            # Should have IGST
            if extracted_data.get('cgst_amount', 0) > 0 or extracted_data.get('sgst_amount', 0) > 0:
                comments.append('CGST/SGST should not be applied for inter-state transactions')

    return comments

# Function to compute overall trust score
def compute_overall_trust_score(extracted_data, ocr_confidence, comments):
    """
    Compute the overall trust score for the extracted data.
    """
    # Number of validations passed
    num_validations = 0
    total_validations = 3  # Adjust based on number of validations

    # If there are comments, validations have failed
    if not comments:
        num_validations = total_validations

    # Field presence check
    required_fields = ['invoice_number', 'invoice_date', 'taxable_value', 'final_amount', 'place_of_supply']
    for field in required_fields:
        if extracted_data.get(field):
            num_validations += 1
        else:
            comments.append(f'Missing field: {field}')

    total_fields = total_validations + len(required_fields)

    # Field validation score
    field_validation_score = num_validations / total_fields

    # Overall trust score as average of OCR confidence and field validation
    overall_trust_score = ((ocr_confidence + field_validation_score) / 2) * 100  # Scale to percentage

    return overall_trust_score, comments