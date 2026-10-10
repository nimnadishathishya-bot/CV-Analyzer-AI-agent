import io
import pypdf
import docx

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text content from PDF file bytes using pypdf.
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        text_content = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
        return "\n".join(text_content).strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text content from DOCX file bytes using python-docx.
    """
    try:
        docx_file = io.BytesIO(file_bytes)
        doc = docx.Document(docx_file)
        text_content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text.strip())
        
        # Also extract text from tables if present
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text_content.append(row_text)
                    
        return "\n".join(text_content).strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

def extract_text_from_file(file_name: str, file_bytes: bytes) -> str:
    """
    Extract text from an uploaded file based on its extension (.pdf or .docx).
    """
    filename_lower = file_name.lower()
    if filename_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith(".docx") or filename_lower.endswith(".doc"):
        return extract_text_from_docx(file_bytes)
    elif filename_lower.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore").strip()
    else:
        raise ValueError(f"Unsupported file format for '{file_name}'. Please upload a PDF or DOCX file.")
