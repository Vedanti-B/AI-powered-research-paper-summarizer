import io
import pdfplumber

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def chunk_text(text: str, max_tokens: int = 400):
    sentences = text.split(". ")
    chunks = []
    current = ""
    for s in sentences:
        if len(current.split()) + len(s.split()) > max_tokens:
            chunks.append(current)
            current = s + ". "
        else:
            current += s + ". "
    if current.strip():
        chunks.append(current)
    return chunks
