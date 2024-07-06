from fpdf import FPDF
from datetime import datetime, timedelta
import json

class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 8)
        self.multi_cell(0, 3, "Amino\n$5 per month\nunlimited invoice creation", align='C')

class InvoiceBot:
    def __init__(self, config_file):
        self.load_config(config_file)
        self.invoice_number = None
        self.invoice_date = datetime.now()
        self.pay_by_date = self.invoice_date + timedelta(days=10)

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            self.config = json.load(file)

    def create_invoice(self):
        self.invoice_number = self.generate_invoice_number()
        return self._create_pdf()

    def generate_invoice_number(self):
        # Generate a random 8-digit invoice number for demo purposes
        import random
        return str(random.randint(10000000, 99999999))

    def _create_pdf(self):
        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Set initial margins to zoom out the PDF
        pdf.set_margins(10, 10, 10)

        # Add logo if provided
        if self.config.get("logo_path"):
            pdf.image(self.config["logo_path"], x=pdf.w - 50, y=10, w=40)

        # Add company details
        pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 10, self.config["company_name"], align='L')
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, self.config["company_address"], align='L')
        pdf.multi_cell(0, 10, self.config["company_contact"], align='L')
        pdf.ln()

        # Invoice details
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Invoice Number: {self.invoice_number}", ln=True)
        pdf.cell(0, 10, f"Invoice Date: {self.invoice_date.strftime('%Y-%m-%d')}", ln=True)
        pdf.cell(0, 10, f"Pay By: {self.pay_by_date.strftime('%Y-%m-%d')}", ln=True)

        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 10, "Must be paid within 10 days, after that a fee of $15 will accrue every additional day.")
        pdf.ln()

        # Customer details
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Bill To:", ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, self.config["customer_name"], align='L')
        pdf.multi_cell(0, 10, self.config["customer_address"], align='L')
        pdf.ln()

        # Table header
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(90, 10, 'Description', 1)
        pdf.cell(35, 10, 'Quantity/Hours', 1)
        pdf.cell(30, 10, 'Unit Price', 1)
        pdf.cell(30, 10, 'Total', 1)
        pdf.ln()

        # Table content
        pdf.set_font('Arial', '', 12)
        for item in self.config["items"]:
            pdf.cell(90, 10, item["description"], 1)
            pdf.cell(35, 10, str(item["quantity"]), 1)
            pdf.cell(30, 10, f"${float(item['unit_price']):.2f}", 1)
            pdf.cell(30, 10, f"${float(item['total']):.2f}", 1)
            pdf.ln()

            # Check if the current page height exceeds the limit and add new page if needed
            if pdf.get_y() > 260:  # Adjust this value as needed to fit your content
                pdf.add_page()

        # Totals
        total_amount = sum(float(item["total"]) for item in self.config["items"])
        pdf.cell(155, 10, 'Total', 1)
        pdf.cell(30, 10, f"${total_amount:.2f}", 1)
        pdf.ln()

        # Payment methods
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Payment Methods:', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"CashApp: {self.config['CashApp']}", ln=True)

        # Add PayPal QR code if provided
        if self.config.get("paypal_qr_path"):
            pdf.image(self.config["paypal_qr_path"], x=pdf.w - 50, y=pdf.get_y(), w=30)
            pdf.ln(30)

        # Signatures
        pdf.set_y(-60)  # Position from bottom of the page
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Signatures:', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Customer: {self.config['signature']}", ln=True)
        pdf.cell(0, 10, f"Merchant: {self.config['merchant_signature']}", ln=True)

        # Save PDF
        invoice_filename = f"{self.invoice_number}.pdf"
        pdf.output(invoice_filename)
        return invoice_filename
