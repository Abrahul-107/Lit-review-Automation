import os
import fitz  # PyMuPDF

def pdf_to_txt(pdf_folder):
    output_folder = f"./{pdf_folder}_txt"
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            doc = fitz.open(pdf_path)

            text = ""
            for page in doc:
                text += page.get_text()

            txt_filename = os.path.splitext(filename)[0] + ".txt"
            txt_path = os.path.join(output_folder, txt_filename)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"Converted {filename} → {txt_filename}")
    return output_folder
