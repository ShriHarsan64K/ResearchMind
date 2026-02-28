import fitz  # PyMuPDF
import os
import re


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract clean text from a PDF file."""
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        full_text += f"\n--- Page {page_num + 1} ---\n{text}"

    doc.close()
    return clean_text(full_text)


def clean_text(text: str) -> str:
    """Clean extracted text — remove extra spaces, weird characters."""
    # Remove multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    # Remove weird unicode characters
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def extract_sections(text: str) -> dict:
    """Try to extract standard paper sections."""
    sections = {
        "abstract": "",
        "introduction": "",
        "methodology": "",
        "results": "",
        "conclusion": "",
        "full_text": text
    }

    # Common section headers in research papers
    patterns = {
        "abstract": r"(?i)abstract[\s\n]+(.*?)(?=\n[A-Z\s]{3,}\n|\Z)",
        "introduction": r"(?i)(?:1\.?\s*)?introduction[\s\n]+(.*?)(?=\n[A-Z\s]{3,}\n|\Z)",
        "methodology": r"(?i)(?:method(?:ology|s)?|approach)[\s\n]+(.*?)(?=\n[A-Z\s]{3,}\n|\Z)",
        "results": r"(?i)(?:results?|experiments?)[\s\n]+(.*?)(?=\n[A-Z\s]{3,}\n|\Z)",
        "conclusion": r"(?i)conclusion[\s\n]+(.*?)(?=\n[A-Z\s]{3,}\n|\Z)",
    }

    for section, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Limit each section to 1500 characters
            sections[section] = match.group(1).strip()[:1500]

    return sections


def get_paper_metadata(pdf_path: str) -> dict:
    """Extract basic metadata from PDF."""
    doc = fitz.open(pdf_path)
    metadata = doc.metadata

    # Try to get title from first page if metadata is empty
    title = metadata.get("title", "")
    if not title:
        first_page = doc.load_page(0)
        first_text = first_page.get_text("text")
        # First non-empty line is usually the title
        lines = [l.strip() for l in first_text.split('\n') if l.strip()]
        title = lines[0] if lines else "Unknown Title"

    doc.close()

    return {
        "title": title or "Unknown Title",
        "author": metadata.get("author", "Unknown Author"),
        "subject": metadata.get("subject", ""),
        "filename": os.path.basename(pdf_path)
    }


def process_pdf(pdf_path: str) -> dict:
    """Main function — process a PDF and return everything."""
    print(f"Processing: {pdf_path}")

    # Extract text
    full_text = extract_text_from_pdf(pdf_path)

    # Extract sections
    sections = extract_sections(full_text)

    # Get metadata
    metadata = get_paper_metadata(pdf_path)

    return {
        "metadata": metadata,
        "sections": sections,
        "char_count": len(full_text),
        "word_count": len(full_text.split())
    }


# Test it directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = process_pdf(sys.argv[1])
        print(f"\nTitle: {result['metadata']['title']}")
        print(f"Author: {result['metadata']['author']}")
        print(f"Words: {result['word_count']}")
        print(f"\nAbstract preview:\n{result['sections']['abstract'][:300]}")
    else:
        print("Usage: python pdf_engine.py <path_to_pdf>")