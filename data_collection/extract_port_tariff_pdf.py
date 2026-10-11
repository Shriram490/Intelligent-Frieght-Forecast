from pypdf import PdfReader
from pathlib import Path
pdf_file = Path("../data/raw/sor-indexed-26-27-final.pdf")

output_file = Path("../data/processed/paradip_sor_2026_27.txt")

print("Reading Paradip Port tariff pdf")

reader = PdfReader(pdf_file)

print("Number of pages:", len(reader.pages))

all_text = []
for page_number , page in enumerate(reader.pages, start = 1):
    text = page.extract_text()
    if text:
        all_text.append(
            f"\n\n===== PAGE {page_number} =====\n\n"
        )
        all_text.append(text)
full_text = "".join(all_text)

output_file.write_text(full_text, encoding="utf-8")

print("\nPDF extraction completed!")
print("Characters extracted:", len(full_text))
print("Output file: ", output_file)
