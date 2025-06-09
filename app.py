from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load email configuration
def load_email_config():
    try:
        with open('email_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

class EmailForm(FlaskForm):
    email_list = FileField('Email List (Excel/CSV)', validators=[FileRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    resume = FileField('Resume (PDF)', validators=[FileRequired()])
    submit = SubmitField('Send Emails')

def send_email(to_email, subject, message, resume_path, config):
    msg = MIMEMultipart()
    msg['From'] = config['email_user']
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach message
    msg.attach(MIMEText(message, 'plain'))

    # Attach resume
    with open(resume_path, 'rb') as f:
        resume = MIMEApplication(f.read(), _subtype='pdf')
        resume.add_header('Content-Disposition', 'attachment', 
                         filename=os.path.basename(resume_path))
        msg.attach(resume)

    # Send email
    try:
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email_user'], config['email_password'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    config = load_email_config()
    
    if not config:
        flash('Please configure email settings first!', 'error')
        return redirect(url_for('configure'))

    if form.validate_on_submit():
        try:
            # Save uploaded files
            email_list_file = secure_filename(form.email_list.data.filename)
            resume_file = secure_filename(form.resume.data.filename)
            
            email_list_path = os.path.join(app.config['UPLOAD_FOLDER'], email_list_file)
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file)
            
            form.email_list.data.save(email_list_path)
            form.resume.data.save(resume_path)

            # Read email list
            if email_list_file.endswith('.csv'):
                df = pd.read_csv(email_list_path)
            else:
                df = pd.read_excel(email_list_path)

            email_column = df.columns[0]  # Assume first column contains emails
            emails = df[email_column].tolist()

            # Send emails
            success_count = 0
            for email in emails:
                if send_email(email, form.subject.data, form.message.data, 
                            resume_path, config):
                    success_count += 1
                    EMAIL_HISTORY.append({'to': email, 'subject': form.subject.data, 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

            flash(f'Successfully sent {success_count} out of {len(emails)} emails!', 'success')
            
            # Cleanup
            os.remove(email_list_path)
            os.remove(resume_path)
            
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('index'))

    return render_template('index.html', form=form)

@app.route('/configure', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        config = {
            'email_user': request.form['email_user'],
            'email_password': request.form['email_password'],
            'smtp_server': request.form['smtp_server'],
            'smtp_port': int(request.form['smtp_port'])
        }
        
        with open('email_config.json', 'w') as f:
            json.dump(config, f)
        
        flash('Email configuration saved successfully!', 'success')
        return redirect(url_for('index'))
    
    config = load_email_config()
    return render_template('configure.html', config=config)

@app.route('/test-connection', methods=['POST'])
def test_connection():
    data = request.json
    email_user = data.get('email_user')
    email_password = data.get('email_password')
    smtp_server = data.get('smtp_server')
    smtp_port = int(data.get('smtp_port', 587))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(email_user, email_password)
        server.quit()
        return jsonify({'success': True, 'message': 'Connection successful!'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Connection failed: {str(e)}'}), 400

TEMPLATES = [
    {
        'key': 'devops',
        'title': 'DevOps Engineer Application',
        'subject': 'Application for DevOps Engineer Position',
        'message': '...'
    },
    {
        'key': 'python',
        'title': 'Python Software Developer Application',
        'subject': 'Application for Python Software Developer Position',
        'message': '...'
    },
    {
        'key': 'kubernetes',
        'title': 'Kubernetes Engineer Application',
        'subject': 'Application for Kubernetes Engineer Position',
        'message': '...'
    },
    {
        'key': 'openstack',
        'title': 'OpenStack Engineer Application',
        'subject': 'Application for OpenStack Engineer Position',
        'message': '...'
    },
    {
        'key': 'ceph',
        'title': 'Ceph Storage Engineer Application',
        'subject': 'Application for Ceph Storage Engineer Position',
        'message': '...'
    },
    {
        'key': 'linux',
        'title': 'Linux Engineer Application',
        'subject': 'Application for Linux Engineer Position',
        'message': '...'
    }
]

# In-memory history (for demo; in production use a DB or file)
EMAIL_HISTORY = []

@app.route('/templates')
def templates_page():
    return render_template('templates.html', templates=TEMPLATES)

@app.route('/history')
def history_page():
    return render_template('history.html', history=EMAIL_HISTORY)

# When sending emails, append to EMAIL_HISTORY
# Example: EMAIL_HISTORY.append({'to': email, 'subject': subject, 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

if __name__ == '__main__':
    app.run(debug=True) 