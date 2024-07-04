import json
import os
from fpdf import FPDF
from datetime import datetime, timedelta

class InvoiceBot:
    def __init__(self, config_file):
        self.load_config(config_file)
        self.invoice_number_file = "invoice_number.txt"
        self.invoice_number = self.get_invoice_number()

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
            self.company_name = config["company_name"]
            self.company_address = config["company_address"]
            self.company_contact = config["company_contact"]
            self.logo_path = config["logo_path"]
            self.customer_name = config["customer_name"]
            self.customer_address = config["customer_address"]
            self.items = config["items"]
            self.paypal = config["paypal"]
            self.paypal_qr_path = config.get("paypal_qr_path", "")
            self.signature = config["signature"]
            self.merchant_signature = config["merchant_signature"]

            # Set the invoice date to the current date
            self.invoice_date = datetime.now().strftime("%Y-%m-%d")
            # Set the 'Pay by' date to 10 days in the future
            self.pay_by_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")

    def get_invoice_number(self):
        if os.path.exists(self.invoice_number_file):
            with open(self.invoice_number_file, 'r') as file:
                invoice_number = int(file.read().strip()) + 1
        else:
            invoice_number = 1
        with open(self.invoice_number_file, 'w') as file:
            file.write(f"{invoice_number:08d}")
        return f"{invoice_number:08d}"

    def create_invoice(self):
        filename = f"invoice_{self.invoice_number}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=5)

        page_width = pdf.w - 2 * pdf.l_margin  # Effective page width

        # Company Details
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 7, self.company_name, 0, 1, 'L')
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 7, self.company_address, 0, 1, 'L')
        pdf.cell(0, 7, self.company_contact, 0, 1, 'L')
        pdf.ln(5)

        # Logo
        if self.logo_path and os.path.exists(self.logo_path):
            pdf.image(self.logo_path, page_width - 33, pdf.get_y() - 25, 30)  # Adjust width and height as needed
        else:
            print(f"Logo file not found at {self.logo_path}")

        # Customer Details
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 7, "Bill To:", 0, 1)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 7, self.customer_name, 0, 1)
        pdf.cell(0, 7, self.customer_address, 0, 1)
        pdf.ln(5)

        # Invoice Number
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 7, f"Invoice Number: {self.invoice_number}", 0, 1)
        pdf.ln(5)

        # Invoice Date
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 7, f"Invoice Date: {self.invoice_date}", 0, 1)
        pdf.ln(5)

        # Pay by Date
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 7, f"Pay by: {self.pay_by_date}", 0, 1)
        pdf.set_font("Arial", '', 8)
        pdf.cell(0, 7, "Must be paid within 10 days. After that, a fee of $15 will accrue every additional day.", 0, 1)
        pdf.ln(5)

        # Items Table
        pdf.set_font("Arial", 'B', 12)
        col_widths = [page_width * 0.5, page_width * 0.15, page_width * 0.15, page_width * 0.2]
        headers = ["Description", "Quantity (hrs)", "Unit Price", "Total"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
        pdf.ln(10)

        pdf.set_font("Arial", '', 12)
        total_amount = 0
        for item in self.items:
            description, quantity, unit_price = item.values()
            total = quantity * unit_price
            total_amount += total
            pdf.cell(col_widths[0], 10, description, 1)
            pdf.cell(col_widths[1], 10, str(quantity), 1, 0, 'R')
            pdf.cell(col_widths[2], 10, f"${unit_price:.2f}", 1, 0, 'R')
            pdf.cell(col_widths[3], 10, f"${total:.2f}", 1, 0, 'R')
            pdf.ln(10)

        pdf.cell(col_widths[0] + col_widths[1] + col_widths[2], 10, "Subtotal", 1)
        pdf.cell(col_widths[3], 10, f"${total_amount:.2f}", 1, 0, 'R')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(col_widths[0] + col_widths[1] + col_widths[2], 10, "Total", 1)
        pdf.cell(col_widths[3], 10, f"${total_amount:.2f}", 1, 0, 'R')
        pdf.ln(15)

        # Payment Details
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 7, "Payment Information", 0, 1)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 7, f"PayPal: {self.paypal}", 0, 1)
        pdf.ln(5)

        # PayPal QR Code
        if self.paypal_qr_path and os.path.exists(self.paypal_qr_path):
            pdf.image(self.paypal_qr_path, 10, pdf.get_y(), 40)  # Adjust x, y, and size as needed
        else:
            print(f"PayPal QR code not found at {self.paypal_qr_path}")
        
        pdf.ln(40)

        # Signatures
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 7, f"Customer Signature: {self.signature}", 0, 1)
        pdf.cell(0, 7, f"Merchant Signature: {self.merchant_signature}", 0, 1)

        pdf.output(filename)
        print(f"Invoice saved as {filename}")

if __name__ == "__main__":
    bot = InvoiceBot("config.json")
    bot.create_invoice()
