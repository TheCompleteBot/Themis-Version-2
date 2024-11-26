import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class UserInterfaceAgent:
    """Handles contract presentation and PDF generation."""

    def __init__(self):
        self.logger = logging.getLogger("themis_logger")
        self.output_dir = "generated_contracts"
        os.makedirs(self.output_dir, exist_ok=True)

    def display_final_contract(self, contract: str) -> str:
        """Generate and save PDF version, return file path."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            pdf_filename = f"contract_{timestamp}.pdf"
            pdf_path = os.path.join(self.output_dir, pdf_filename)
            self._create_pdf(contract, pdf_path)
            self.logger.info(f"Contract saved as {pdf_path}")
            print("Hello PDF Path : ",pdf_path)
            return pdf_path
        except Exception as e:
            self.logger.error(f"Error generating PDF: {str(e)}")
            raise

    def _create_pdf(self, content: str, path: str) -> None:
        """Create PDF from contract content."""
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(path, pagesize=letter)
        story = []

        # Process content into paragraphs
        for line in content.split('\n\n'):
            story.append(Paragraph(line.strip(), styles['Normal']))
            story.append(Spacer(1, 12))

        doc.build(story)
