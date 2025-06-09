# Bulk Email Sender

A modern web application for sending bulk emails with resume attachments. Built with Flask and featuring a clean, responsive UI.

## Features

- Send bulk emails with resume attachments
- Support for Excel and CSV email lists
- Secure email configuration
- Modern, responsive UI
- Real-time feedback on email sending status

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your email settings:
   - For Gmail users:
     1. Enable 2-factor authentication in your Google Account
     2. Generate an App Password (Google Account → Security → App Passwords)
     3. Use this App Password in the application

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. First, click on "Configure Email" in the navigation bar and enter your email settings
2. On the main page:
   - Upload an Excel or CSV file containing email addresses (first column)
   - Enter the email subject
   - Write your message
   - Upload your resume (PDF)
   - Click "Send Emails"

## Email List Format

The application expects an Excel or CSV file with email addresses in the first column. Example:

```
email
john@example.com
jane@example.com
```

## Security Notes

- Email credentials are stored locally in `email_config.json`
- Files are automatically deleted after sending
- The application uses secure SMTP with TLS
- Maximum file upload size is limited to 16MB

## Requirements

- Python 3.7+
- Modern web browser
- Internet connection for email sending 