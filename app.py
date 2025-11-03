from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Important for session login

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATA_FILE = 'mobile_data.json'
FEEDBACK_FILE = 'feedback.json'

def load_mobile_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_mobile_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_feedback_data():
    try:
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_feedback_data(data):
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def price_in_range(mobile_price, selected_price_range):
    if selected_price_range == "Choose" or not selected_price_range:
        return True

    if not mobile_price:
        return False

    price_str = str(mobile_price).lower().replace('₹', '').replace(',', '').strip()

    try:
        if 'k' in price_str:
            price = int(float(price_str.replace('k', '')) * 1000)
        else:
            price = int(float(price_str))
    except (ValueError, TypeError):
        return False

    price_ranges = {
        "Under 10k": (0, 10000),
        "10k - 15k": (10000, 15000),
        "15k - 20k": (15000, 20000),
        "20k - 30k": (20000, 30000)
    }

    if selected_price_range in price_ranges:
        min_price, max_price = price_ranges[selected_price_range]
        return min_price <= price <= max_price

    return True

# ✅ ADMIN LOGIN ROUTE
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Hardcoded login
        if username == "admin" and password == "7882":
            session["admin_logged"] = True
            return redirect(url_for("admin_upload"))

        return "Invalid Credentials", 401

    return render_template("admin_login.html")


@app.route("/logout")
def logout():
    session.pop("admin_logged", None)
    return redirect(url_for("admin_login"))


@app.route('/admin-upload')
def admin_upload():
    if not session.get("admin_logged"):
        return redirect(url_for("admin_login"))
    return render_template('input.html')


@app.route('/upload-target', methods=['POST'])
def upload_target():
    if not session.get("admin_logged"):
        return redirect(url_for("admin_login"))

    try:
        name = request.form.get('name', '').strip()
        price = request.form.get('price', '').strip()
        ram = request.form.get('ram', '').strip()
        storage = request.form.get('storage', '').strip()
        processor = request.form.get('processor', '').strip()
        camera = request.form.get('camera', '').strip()
        battery = request.form.get('battery', '').strip()
        charging = request.form.get('charging', '').strip()
        speciality = request.form.get('speciality', '').strip()

        image_filename = None
        if 'uploadedFile' in request.files:
            file = request.files['uploadedFile']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        mobile_data = {
            'Name': name,
            'Price': price,
            'RAM': ram,
            'Storage': storage,
            'Processor': processor,
            'Camera': camera,
            'Battery': battery,
            'Charging': charging,
            'Speciality': speciality,
            'Image': image_filename
        }

        all_data = load_mobile_data()
        all_data.append(mobile_data)
        save_mobile_data(all_data)

        return redirect(url_for('result_page'))

    except Exception as e:
        return f"Error occurred: {str(e)}", 500


@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        if not message:
            return "Message is required", 400

        feedback_data = {
            'name': name if name else 'Anonymous',
            'email': email if email else 'Not provided',
            'message': message,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        all_feedback = load_feedback_data()
        all_feedback.append(feedback_data)
        save_feedback_data(all_feedback)

        # Redirect back to search page with success message
        return redirect(url_for('search_success'))

    except Exception as e:
        return f"Error occurred while submitting feedback: {str(e)}", 500


@app.route('/search-success')
def search_success():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Feedback Submitted</title>
        <style>
            body { 
                font-family: 'Poppins', sans-serif; 
                background: linear-gradient(135deg, #f8d7ff, #ffe0e0);
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0; 
            }
            .success-message { 
                background: white; 
                padding: 40px; 
                border-radius: 16px; 
                text-align: center; 
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            }
            .success-message h1 { 
                color: #4A00E0; 
            }
            .btn { 
                display: inline-block; 
                padding: 12px 24px; 
                background: linear-gradient(135deg, #4A00E0, #8E2DE2); 
                color: white; 
                text-decoration: none; 
                border-radius: 50px; 
                margin-top: 20px; 
            }
        </style>
    </head>
    <body>
        <div class="success-message">
            <h1>✅ Thank You!</h1>
            <p>Your feedback has been submitted successfully.</p>
            <a href="{{ url_for('search') }}" class="btn">Back to Search</a>
        </div>
    </body>
    </html>
    """


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        price_filter = request.form.get('price', 'Choose')
        ram_filter = request.form.get('ram', 'Choose')
        storage_filter = request.form.get('storage', 'Choose')
        speciality_filter = request.form.get('speciality', 'Choose')

        all_mobiles = load_mobile_data()
        filtered_mobiles = []

        for mobile in all_mobiles:
            # Price filter
            if price_filter != "Choose" and not price_in_range(mobile.get('Price', ''), price_filter):
                continue
            
            # RAM filter - check if RAM value contains the filter value
            if ram_filter != "Choose" and ram_filter not in mobile.get('RAM', ''):
                continue
            
            # Storage filter - check if Storage value contains the filter value
            if storage_filter != "Choose" and storage_filter not in mobile.get('Storage', ''):
                continue
            
            # Speciality filter - case insensitive partial match
            if speciality_filter != "Choose" and speciality_filter.lower() not in mobile.get('Speciality', '').lower():
                continue

            filtered_mobiles.append(mobile)

        return render_template('result.html', results=filtered_mobiles, is_search=True)

    return render_template('search.html')


@app.route('/results')
def result_page():
    all_data = load_mobile_data()
    return render_template('result.html', results=all_data, is_search=False)


@app.route('/')
def home():
    return redirect(url_for("search"))


if __name__ == '__main__':
    app.run(debug=True)

