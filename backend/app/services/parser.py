import pypdf
import io

def extract_text_from_pdf(file_bytes: bytes)->str:
    """Takes raw PDF bytes, returns extracted txt strs
       Raises ValueError if PDF is empty or unreadable.
    """
    try:
        pdf_reader =  pypdf.PdfReader(io.BytesIO(file_bytes))

        if len(pdf_reader.pages) == 0:
            raise ValueError("PDF has no pages")
        

        text= ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text+=page_text + "\n"

        text=" ".join(text.split())


        if not text.strip():
            raise ValueError("Could not extract any text. PDF might be image-based.")
        
        return text
    
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")

