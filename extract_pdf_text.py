import sys
from pdfminer.high_level import extract_text

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python extract_pdf_text.py <pdf_path>')
        sys.exit(1)
    pdf_path = sys.argv[1]
    text = extract_text(pdf_path)
    print(text.encode('utf-8', errors='replace').decode('utf-8'))
