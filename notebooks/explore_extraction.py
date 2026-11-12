import pdfplumber

pdf_path = "data/raw/circulaire_bourses_2026-2027.pdf"

with pdfplumber.open(pdf_path) as pdf:       # ouvre le PDF, le referme seul à la fin
    print("Nombre de pages :", len(pdf.pages))
    for i in range(len(pdf.pages)):
        page = pdf.pages[i]
        print("Numéro de page :", page.page_number)   # affiche 1, 2, 3, ...
        print(page.extract_text())
    