from img2table.document import PDF
from img2table.ocr import TesseractOCR
import pandas as pd
from PyPDF2 import PdfWriter, PdfReader
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/get_score", methods=["POST"])
def get_score():   
    try:
        if 'pdf' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['pdf']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file:
            inputpdf = PdfReader(file.stream)
            output_dir = 'recurzive/model/scraper/pages'

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for i in range(len(inputpdf.pages)):
            output = PdfWriter()
            output.add_page(inputpdf.pages[i])
            with open(f'{output_dir}/document-page{i}.pdf', 'wb') as outputStream:
                output.write(outputStream)

        all_tables = pd.DataFrame()

        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            
            if filename.endswith('.pdf'):
                pdf = PDF(src=file_path)
                
                ocr = TesseractOCR(lang='eng')
                
                temp_xlsx = 'recurzive/model/scraper/temp_tables.xlsx'
                pdf.to_xlsx(temp_xlsx, ocr=ocr)
                
                df = pd.read_excel(temp_xlsx)
                
                all_tables = pd.concat([all_tables, df], ignore_index=True)

        final_xlsx = 'recurzive/model/scraper/final_tables.xlsx'
        all_tables.to_excel(final_xlsx, index=False)


        df = pd.read_excel('/home/haideraqeeb-pc/code/recurzive/recurzive/model/scraper/recurzive/model/scraper/final_tables.xlsx')
        df["Credit"] = df["Credit"].str.replace(',', '')
        df["Credit"] = df["Credit"].astype(float)
        sum = df["Credit"].sum()

        score = []
        score.append({"income":sum})

        return jsonify(score)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/get_history", methods=["GET"])
def get_history():
    df = pd.read_excel('/home/haideraqeeb-pc/code/recurzive/recurzive/model/scraper/recurzive/model/scraper/final_tables.xlsx')
    ret = df.to_dict(orient="records")
    return jsonify(ret) 
    

    return ret


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)