import os
import sys
from PIL import Image
from google import genai
from google.genai import types
from app.config import config

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text content from a PDF file using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        text_parts = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- Page {i + 1} ---\n{page_text}")
        return "\n\n".join(text_parts).strip()
    except Exception as e:
        return f"[PDF Extraction Error: {str(e)}]"

def extract_text_from_docx(file_path: str) -> str:
    """Extracts text, paragraphs, and tables from a Word document (.docx)."""
    try:
        import docx
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        # Extract tables if any
        table_texts = []
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    table_texts.append(row_text)

        full_content = "\n\n".join(paragraphs)
        if table_texts:
            full_content += "\n\n--- Tables ---\n" + "\n".join(table_texts)
        return full_content.strip()
    except Exception as e:
        return f"[DOCX Extraction Error: {str(e)}]"

def extract_text_from_plain(file_path: str) -> str:
    """Reads plain text, code, csv, or markdown files with encoding fallback."""
    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read().strip()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return f"[File Read Error: {str(e)}]"
    return "[Could not decode file with supported text encodings]"

def analyze_document(file_path: str, query: str = "Please summarize the key contents and details of this document.") -> str:
    """
    Analyzes an uploaded or referenced document (PDF, Word DOCX, PNG/JPG image, or text file)
    using Gemini multimodal intelligence with local fallback.
    """
    clean_path = file_path.strip().strip('"').strip("'")
    if not os.path.exists(clean_path):
        return f"I cannot find the file at '{file_path}', Boss. Please verify the path."

    ext = os.path.splitext(clean_path)[1].lower()
    file_name = os.path.basename(clean_path)

    # Tactical prompt instruction
    system_instruction = (
        f"You are F.R.I.D.A.Y., a tactical personal AI assistant with an Irish female persona. "
        f"The user has attached the file '{file_name}' and asked: '{query}'. "
        f"Provide a clear, accurate, and structured answer based strictly on the document contents. "
        f"Keep your spoken opening concise and direct (1-2 sentences), followed by the specific details requested. Address the user as Boss."
    )

    client = genai.Client(api_key=config.GEMINI_API_KEY) if config.GEMINI_API_KEY else None

    # 1. Image Files (PNG, JPG, JPEG, WEBP, BMP)
    if ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]:
        try:
            img = Image.open(clean_path)
            # Optimize image size for API payload
            img.thumbnail((1600, 1600))
            if client:
                response = client.models.generate_content(
                    model=config.GEMINI_MODEL,
                    contents=[img, f"{system_instruction}\n\nUser Question: {query}"]
                )
                return response.text.strip() if response and response.text else "Image analyzed, Boss."
        except Exception as e:
            return f"Error analyzing image '{file_name}': {str(e)}"

    # 2. PDF Documents (.pdf)
    if ext == ".pdf":
        # First try native Gemini multimodal PDF ingestion
        try:
            if client and os.path.getsize(clean_path) < 20 * 1024 * 1024:  # under 20MB
                with open(clean_path, "rb") as f:
                    pdf_bytes = f.read()
                pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
                response = client.models.generate_content(
                    model=config.GEMINI_MODEL,
                    contents=[pdf_part, f"{system_instruction}\n\nUser Question: {query}"]
                )
                if response and response.text:
                    return response.text.strip()
        except Exception as e:
            print(f"[Gemini Native PDF Ingestion Notice] {e}. Falling back to text extraction...")

        # Fallback: Extract text via pypdf
        extracted_text = extract_text_from_pdf(clean_path)
        if not extracted_text or extracted_text.startswith("[PDF Extraction Error"):
            return f"I had difficulty extracting readable text from '{file_name}', Boss. It might be scanned or encrypted."

        # Truncate text if massive (keep within prompt token comfort)
        trimmed_text = extracted_text[:40000]
        if client:
            try:
                response = client.models.generate_content(
                    model=config.GEMINI_MODEL,
                    contents=[f"{system_instruction}\n\nDocument Text:\n{trimmed_text}\n\nUser Question: {query}"]
                )
                return response.text.strip() if response and response.text else "PDF content analyzed, Boss."
            except Exception as e:
                return f"PDF analysis error: {str(e)}"

    # 3. Word Documents (.docx)
    if ext in [".docx", ".doc"]:
        extracted_text = extract_text_from_docx(clean_path)
        if not extracted_text or extracted_text.startswith("[DOCX Extraction Error"):
            return f"Could not read Word document '{file_name}', Boss: {extracted_text}"

        trimmed_text = extracted_text[:40000]
        if client:
            try:
                response = client.models.generate_content(
                    model=config.GEMINI_MODEL,
                    contents=[f"{system_instruction}\n\nDocument Text:\n{trimmed_text}\n\nUser Question: {query}"]
                )
                return response.text.strip() if response and response.text else "Word document analyzed, Boss."
            except Exception as e:
                return f"Document analysis error: {str(e)}"

    # 4. Text / Code / CSV / Markdown (.txt, .py, .csv, .json, .md)
    if ext in [".txt", ".py", ".csv", ".json", ".md", ".log", ".html", ".js", ".css"]:
        extracted_text = extract_text_from_plain(clean_path)
        trimmed_text = extracted_text[:40000]
        if client:
            try:
                response = client.models.generate_content(
                    model=config.GEMINI_MODEL,
                    contents=[f"{system_instruction}\n\nFile Content:\n{trimmed_text}\n\nUser Question: {query}"]
                )
                return response.text.strip() if response and response.text else f"File '{file_name}' processed, Boss."
            except Exception as e:
                return f"File analysis error: {str(e)}"

    return f"Unsupported file type '{ext}' for '{file_name}', Boss. Supported formats: PDF, DOCX, PNG, JPG, WEBP, TXT, CSV, Code."
