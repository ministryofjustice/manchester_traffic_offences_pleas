from io import BytesIO
from xhtml2pdf import pisa


class PDFUtils:

    @staticmethod
    def create_pdf_from_html(html: str) -> BytesIO:
        pdf_stream: BytesIO = BytesIO()
        pisa.CreatePDF(html, dest=pdf_stream)
        pdf_stream.seek(0)
        return pdf_stream
