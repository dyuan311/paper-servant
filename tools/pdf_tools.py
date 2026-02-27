from typing import Optional
from pathlib import Path
from agno.tools import Toolkit
import pypdf

class PDFTools(Toolkit):
    def __init__(self):
        super().__init__(name="pdf_tools")
        self.register(self.read_pdf)

    def read_pdf(self, pdf_path: str, max_pages: int = 20) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file.
            max_pages (int): Maximum number of pages to read (default 20).
            
        Returns:
            str: Extracted text content.
        """
        path = Path(pdf_path)
        if not path.exists():
            return f"Error: File not found at {pdf_path}"
            
        try:
            reader = pypdf.PdfReader(path)
            text = []
            
            # Read pages
            count = 0
            for page in reader.pages:
                if count >= max_pages:
                    break
                content = page.extract_text()
                if content:
                    text.append(content)
                count += 1
                
            full_text = "\n\n".join(text)
            
            if not full_text.strip():
                return "Warning: No text could be extracted from this PDF. It might be scanned or encrypted."
                
            return full_text
            
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
