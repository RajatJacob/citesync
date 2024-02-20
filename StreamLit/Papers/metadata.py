import PyPDF2

def extract_metadata(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfFileReader(pdf_file)
        metadata = reader.getDocumentInfo()
        return metadata

# Replace 'your_pdf.pdf' with the path to your PDF file
pdf_metadata = extract_metadata('A_new_method_for_demand_response_by_real-time_pricing_signals_for_lighting_loads.pdf')
print(pdf_metadata)