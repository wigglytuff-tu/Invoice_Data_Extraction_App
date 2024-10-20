# app.py
import streamlit as st
import pandas as pd
from main import process_pdf
import tempfile
import os

st.title("Invoice Data Extraction")

st.markdown("""
Upload multiple PDF files, and extract invoice data with comments and validation results.
""")

uploaded_files = st.file_uploader("Choose PDF files", type=['pdf'], accept_multiple_files=True)

if uploaded_files:
    records = []
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(uploaded_file.read())
            temp_pdf_path = temp_pdf.name

        st.write(f"Processing file: {uploaded_file.name}")
        data = process_pdf(temp_pdf_path)
        records.append(data)

        # Display comments and progress
        st.write(f"OCR Confidence Level: {data.get('ocr_confidence', 0):.2f}%")
        st.write(f"Overall Trust Score: {data.get('overall_trust_score', 0):.2f}%")
        if data.get('comments'):
            st.write(f"Comments: {data.get('comments')}")
        else:
            st.write("No validation issues found.")
        st.write("---")

        # Remove the temporary file
        os.unlink(temp_pdf_path)

    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Display the DataFrame
    st.subheader("Extracted Data")
    st.dataframe(df)

    # Provide option to download the data as Excel or CSV
    output_format = st.selectbox("Select output format", ["CSV", "Excel"])
    if output_format == "CSV":
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='extracted_invoice_data.csv',
            mime='text/csv',
        )
    else:
        towrite = pd.ExcelWriter("extracted_invoice_data.xlsx", engine='xlsxwriter')
        df.to_excel(towrite, index=False)
        towrite.save()
        with open("extracted_invoice_data.xlsx", "rb") as f:
            st.download_button(
                label="Download data as Excel",
                data=f,
                file_name='extracted_invoice_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
