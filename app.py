from flask import Flask, render_template, request, send_file
import json
import os
from werkzeug.utils import secure_filename
from main import InvoiceBot
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file uploads
        logo_path = ""
        paypal_qr_path = ""

        if 'logo' in request.files and request.files['logo'].filename != '':
            logo_file = request.files['logo']
            if allowed_file(logo_file.filename):
                logo_filename = secure_filename(logo_file.filename)
                logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
                logo_file.save(logo_path)

        if 'paypal_qr' in request.files and request.files['paypal_qr'].filename != '':
            paypal_qr_file = request.files['paypal_qr']
            if allowed_file(paypal_qr_file.filename):
                paypal_qr_filename = secure_filename(paypal_qr_file.filename)
                paypal_qr_path = os.path.join(app.config['UPLOAD_FOLDER'], paypal_qr_filename)
                paypal_qr_file.save(paypal_qr_path)

        # Collect form data
        items = []
        descriptions = request.form.getlist('description')
        quantities = request.form.getlist('quantity')
        unit_prices = request.form.getlist('unit_price')

        for description, quantity, unit_price in zip(descriptions, quantities, unit_prices):
            item_total = float(quantity) * float(unit_price)
            items.append({
                "description": description,
                "quantity": quantity,
                "unit_price": unit_price,
                "total": item_total
            })

        data = {
            "company_name": request.form['company_name'],
            "company_address": request.form['company_address'],
            "company_contact": request.form['company_contact'],
            "logo_path": logo_path,
            "customer_name": request.form['customer_name'],
            "customer_address": request.form['customer_address'],
            "items": items,
            "paypal": request.form['paypal'],
            "paypal_qr_path": paypal_qr_path,
            "signature": request.form['signature'],
            "merchant_signature": request.form['merchant_signature']
        }

        # Save data to config.json
        with open('config.json', 'w') as config_file:
            json.dump(data, config_file, indent=4)

        # Create invoice
        bot = InvoiceBot('config.json')
        invoice_filename = bot.create_invoice()

        # Send invoice file to user
        return send_file(invoice_filename, as_attachment=True)

    return render_template('index.html')

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
