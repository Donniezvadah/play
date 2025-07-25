from pdfminer.high_level import extract_text
import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python extract_pdf_text_to_file.py <pdf_path> <output_txt_path>')
        sys.exit(1)
    pdf_path = sys.argv[1]
    output_txt_path = sys.argv[2]
    text = extract_text(pdf_path)
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Extracted text to {output_txt_path}")
