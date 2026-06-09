from docx import Document
p = "Group11_Movie_Genre_Classification_and_Recommendation_Report.docx"
doc = Document(p)
with open("doc_paragraphs.txt", "w", encoding="utf-8") as out:
    for i, para in enumerate(doc.paragraphs):
        txt = para.text.replace("\n", "\\n")
        out.write(f"{i}: {txt}\n")
print("WROTE doc_paragraphs.txt")
