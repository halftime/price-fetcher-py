import fitz  # PyMuPDF

pdf_path = "Infofiche Argenta Pensioenspaarfonds (1).pdf"
doc = fitz.open(pdf_path)

for i in range(len(doc)):
    page_text = doc[i].get_text()
    if "GECUMULEERD RENDEMENT OVER DE LAATSTE 10 JAAR" in page_text:
        page = doc[i]
        break

# extract first image on the page (the graph)
image_list = page.get_images(full=True)
xref = image_list[0][0]

pix = fitz.Pixmap(doc, xref)
out_file = "argenta_cum_return_graph.png"
pix.save(out_file)

print("Saved graph to:", out_file)
