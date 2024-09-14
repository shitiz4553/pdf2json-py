from flask import Flask, request, jsonify
import pdfplumber
import pandas as pd
import json
from flask_cors import CORS  # To allow CORS

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from other origins (like your React Native app)

# Route to check if the server is running
@app.route('/')
def home():
    return "Server running"

@app.route('/extract-pdf', methods=['POST'])
def extract_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400

    pdf_file = request.files['pdf']
    data = []

    # Open and process the PDF file
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Extract text from the page
            page_text = page.extract_text()
            
            # Extract tables from the page (if any)
            tables = page.extract_tables()
            tables_data = []
            
            for table_num, table in enumerate(tables):
                # Convert table to a DataFrame for better organization
                df = pd.DataFrame(table[1:], columns=table[0])
                table_dict = df.to_dict(orient='records')
                tables_data.append({
                    "table_number": table_num + 1,
                    "content": table_dict
                })
            
            # Append both text and table data for the current page
            data.append({
                "page": page_num + 1,
                "text": page_text if page_text else "No text content",
                "tables": tables_data if tables_data else "No table content"
            })

    return jsonify(data)

if __name__ == '__main__':
    # Run the Flask app on '0.0.0.0' to allow access from other devices on the network
    app.run(debug=True)
