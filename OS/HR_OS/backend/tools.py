import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

def ocr_pdf(pdf_path):
    mistral_key = os.getenv("MISTRAL_API_KEY")

    client = Mistral(api_key=mistral_key)
    
    # check if the file exists
    if not os.path.exists(pdf_path):
        print("PDF file not found")
        return
    
    uploaded_pdf = client.files.upload(
        file={
            "file_name": pdf_path,
            "content": open(pdf_path, "rb"),
        },
        purpose="ocr"
    )

    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)

    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url.url,
        },
        include_image_base64=True
    )

    with open(f"MarkdownResumes/{pdf_path.split('/')[-1].split('.')[0]}.md", "w") as f:
        f.write("\n".join([page.markdown for page in ocr_response.pages]))