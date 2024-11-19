from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# API endpoint to check the service status
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Notification service is running"})

# API endpoint to send an email notification
@app.route('/notify', methods=['POST'])
def notify():
    try:
        # Extract notification and email credentials from the request
        data = request.get_json()
        recipient = data['recipient']
        subject = data['subject']
        message = data['message']
        email_address = data['email_address']
        email_password = data['email_password']

        # SMTP configuration
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587

        # Create the email
        msg = MIMEText(message)
        msg['From'] = email_address
        msg['To'] = recipient
        msg['Subject'] = subject

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.sendmail(email_address, recipient, msg.as_string())

        return jsonify({"message": "Notification sent successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
