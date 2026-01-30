import pandas as pd
import PyPDF2
import json
import os

def analyze_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return {
            "columns": df.columns.tolist(),
            "first_rows": df.head(3).to_dict(orient='records'),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
    except Exception as e:
        return {"error": str(e)}

def analyze_pdf(file_path):
    try:
        text_content = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
        return text_content
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def main():
    base_dir = r"c:\Users\shyam\Documents\VS CODE\GEN AI\Inventory_Assets Management"
    excel_path = os.path.join(base_dir, "Inventory_dataset.xlsx")
    pdf_path = os.path.join(base_dir, "Detailed Development Plan.pdf")

    results = {}
    
    print("Analyzing Excel...")
    results['excel'] = analyze_excel(excel_path)
    
    print("Analyzing PDF...")
    results['pdf_text'] = analyze_pdf(pdf_path)

    print("\n--- ANALYSIS RESULTS ---")
    print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    main()
