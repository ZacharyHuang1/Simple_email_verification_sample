import random
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com' 
app.config['MAIL_PASSWORD'] = 'your_password' 

mail = Mail(app)
verification_code = None

# Abstract API settings
API_URL = "https://emailvalidation.abstractapi.com/v1/"
API_KEY = "" 


@app.route("/", methods=["GET", "POST"])
def index():
    global verification_code
    if request.method == "POST":
        email = request.form.get("email")
        
        # Get Abstract API
        try:
            response = requests.get(f"{API_URL}?api_key={API_KEY}&email={email}")
            print(response.status_code)  # status code
            print(response.content)      # return API content
            
            # API response data
            data = response.json()
            
            # Validate the email
            if not data.get("is_valid_format", {}).get("value") or not data.get("is_smtp_valid", {}).get("value"):
                flash("Email is in invalid form")
                return redirect(url_for("index"))
            if data.get("is_disposable_email", {}).get("value"):
                flash("You can't use disposable email")
                return redirect(url_for("index"))

        except requests.exceptions.RequestException as e:
            flash(f"Email service unavailable：{e}")
            return redirect(url_for("index"))

        # Generate the verification code
        verification_code = str(random.randint(100000, 999999))

        # Send the veri code
        try:
            msg = Message("Email Verification code", sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f"Your code is：{verification_code}"
            mail.send(msg)
            flash("Sent! Please check your email")
            return redirect(url_for("verify", email=email))
        except Exception as e:
            flash(f"Fail to send：{e}")
            return redirect(url_for("index"))
    return render_template("index.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    global verification_code
    if request.method == "POST":
        user_code = request.form.get("code")
        if user_code == verification_code:
            flash("Verified successuflly！")
            return redirect(url_for("index"))
        else:
            flash("Code Error, please try again！")
    return render_template("verify.html")


if __name__ == "__main__":
    app.run(debug=True)