import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.pdf_parser import PDFParser

# Test PDF file
import os
pdf_dir = os.path.join(os.path.dirname(__file__), 'uploads')
# Try different PDF files to find an actual academic paper
pdf_file = os.path.join(pdf_dir, "20260113130916_Prompt.pdf")
if os.path.exists(pdf_file):
    print(f"Testing PDF: {pdf_file}")
    print(f"File size: {os.path.getsize(pdf_file)} bytes")

    parser = PDFParser(pdf_file)
    result = parser.parse()

    print(f"\n=== Parse Result ===")
    print(f"Title: {len(result.get('title', ''))} chars")
    print(f"Authors: {len(result.get('authors', ''))} chars")
    print(f"Abstract: {len(result.get('abstract', ''))} chars")
    print(f"Keywords: {len(result.get('keywords', ''))} chars")
    print(f"Sections: {len(result.get('sections', ''))} chars")

    # Show first 200 chars of extracted text
    if result.get('title'):
        print(f"\nTitle preview: {result.get('title', '')[:100]}")
    if result.get('abstract'):
        print(f"Abstract preview: {result.get('abstract', '')[:200]}")

    # Show sections data for debugging
    try:
        import json
        sections = json.loads(result.get('sections', '[]'))
        print(f"\n=== Sections ({len(sections)} found) ===")
        for i, section in enumerate(sections[:3]):  # Show first 3 sections
            print(f"Section {i+1}: {section.get('number', 'N/A')} {section.get('title', 'N/A')}")
            print(f"  Content preview: {section.get('content', '')[:100]}...")
    except Exception as e:
        print(f"Error parsing sections: {e}")
else:
    print(f"File not found: {pdf_file}")
