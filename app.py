# app.py
from flask import Flask, render_template, request, jsonify
import subprocess
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)
attendance_process = None  # Global variable to store the subprocess

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-attendance')
def check_attendance():
    subject = request.args.get('subject')
    period = request.args.get('period')
    date_str = datetime.now().strftime('%Y-%m-%d')

    # Setup Google Sheet
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    try:
        sheet = client.open("Face_Attendance").worksheet(date_str)
        data = sheet.get_all_records()
        prev = next((r for r in data if r['Subject'].lower() == subject.lower()), None)
        if prev:
            return jsonify({"exists": True, "prevPeriod": prev["Period"]})
    except:
        pass

    return jsonify({"exists": False})

@app.route('/start-attendance')
def start_attendance():
    global attendance_process
    subject = request.args.get('subject')
    period = request.args.get('period')
    reuse = request.args.get('reuse', 'false') == 'true'

    if attendance_process and attendance_process.poll() is None:
        return "Attendance process is already running."

    try:
        attendance_process = subprocess.Popen(
            ['python', 'face_attendance.py', subject, period, str(reuse)]
        )
        return "Attendance started. Webcam will open shortly."
    except Exception as e:
        return f"Error: {e}"

@app.route('/stop-attendance')
def stop_attendance():
    global attendance_process
    if attendance_process and attendance_process.poll() is None:
        attendance_process.terminate()
        attendance_process = None
        return "Attendance stopped."
    else:
        return "No attendance process running."

if __name__ == "__main__":
    app.run(debug=True)
