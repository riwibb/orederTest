from flask import Flask, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect
import csv
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
csrf = CSRFProtect(app)

CSV_FILE = 'data.csv'

def phone_exists(phone_number):
    if not os.path.exists(CSV_FILE):
        return False
    
    with open(CSV_FILE, 'r') as file:
        csv_reader = csv.DictReader(file)
        return any(row['Phone Number'] == phone_number for row in csv_reader)

@app.route('/check_phone', methods=['POST'])
def check_phone():
    phone = request.form.get('phone')
    exists = phone_exists(phone)
    return jsonify({'exists': exists})

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Check required fields
            if 'name' not in request.form or 'phone' not in request.form:
                return "Name and phone are required", 400

            name = request.form['name']
            phone = request.form['phone']
            
            # Get counts (default to 0 if not selected)
            beef_count = request.form.get('beef_count', '0')
            goat_count = request.form.get('goat_count', '0')
            sheep_count = request.form.get('sheep_count', '0')
            orphanage_count = request.form.get('orphanage_count', '0')
            sylhet_count = request.form.get('sylhet_count', '0')
            total_amount = request.form.get('total_amount', '0')
            
            # Validate phone
            if not phone.isdigit() or len(phone) != 10:
                return "Invalid phone number", 400
                
            if phone_exists(phone):
                return "Phone number already exists", 400

            # Validate that at least one item is selected
            if all(count == '0' for count in [beef_count, goat_count, sheep_count, 
                                            orphanage_count, sylhet_count]):
                return "Please select at least one item", 400

            # Create file if it doesn't exist
            file_exists = os.path.exists(CSV_FILE)
            
            with open(CSV_FILE, 'a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(['Name', 'Phone Number', 'Beef Count', 'Goat Count', 
                                   'Sheep Count', 'Orphanage Donation Count', 
                                   'Sylhet Donation Count', 'Total Amount'])
                writer.writerow([name, phone, beef_count, goat_count, sheep_count, 
                               orphanage_count, sylhet_count, total_amount])
            
            return "Order submitted successfully!", 200
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
