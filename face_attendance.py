#google_Sheet_writer.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/creds.json", scope)
client = gspread.authorize(creds)

SHEET_NAME = "Face_Attendance"

def has_existing_attendance(subject, date_str):
    try:
        sheet = client.open(SHEET_NAME)
        worksheet = sheet.worksheet(date_str)
        records = worksheet.get_all_records()
        return any(row.get("Subject", "").lower() == subject.lower() for row in records)
    except:
        return False

def copy_attendance_if_exists(prev_period, curr_period, subject, date_str):
    sheet = client.open(SHEET_NAME)
    try:
        worksheet = sheet.worksheet(date_str)
    except:
        worksheet = sheet.add_worksheet(title=date_str, rows="1000", cols="4")
        worksheet.append_row(["Name", "Subject", "Period", "Time"])

    records = worksheet.get_all_records()

    # 🛡️ Avoid duplicate copying
    existing_names = {
        row["Name"]
        for row in records
        if str(row.get("Period")) == str(curr_period) and row.get("Subject", "").lower() == subject.lower()
    }

    copied = False
    for row in records:
        if str(row.get("Period")) == str(prev_period) and row.get("Subject", "").lower() == subject.lower():
            if row["Name"] not in existing_names:
                worksheet.append_row([
                    row["Name"], subject, curr_period, datetime.now().strftime('%H:%M:%S')
                ])
                copied = True

    if copied:
        print(f"[INFO] Attendance copied from Period {prev_period} for subject '{subject}'.")
    else:
        print(f"[INFO] No new names copied — all entries already exist for Period {curr_period}.")


def mark_attendance(name, subject, period):
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')

    sheet = client.open(SHEET_NAME)
    try:
        worksheet = sheet.worksheet(date_str)
    except:
        worksheet = sheet.add_worksheet(title=date_str, rows="1000", cols="4")
        worksheet.append_row(["Name", "Subject", "Period", "Time"])

    records = worksheet.get_all_records()

    if len(records) == 0:
        worksheet.append_row(["Name", "Subject", "Period", "Time"])

    for row in records:
        if row["Name"] == name and str(row["Period"]) == str(period) and row["Subject"].lower() == subject.lower():
            print(f"[INFO] Already marked: {name} for {subject} - Period {period}")
            return

    worksheet.append_row([name, subject, period, time_str])
    print(f"[SUCCESS] Marked {name} for {subject} - Period {period} at {time_str}")





# face_attendance.py
import cv2, face_recognition, numpy as np, os, sys
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# CLI args
subject = sys.argv[1]
period = sys.argv[2]
reuse_flag = sys.argv[3].lower() == 'true'
date_str = datetime.now().strftime('%Y-%m-%d')

# Google Sheet Auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Face_Attendance")
try:
    worksheet = sheet.worksheet(date_str)
except:
    worksheet = sheet.add_worksheet(title=date_str, rows="1000", cols="4")
    worksheet.append_row(["Name", "Subject", "Period", "Time"])

if reuse_flag:
    data = worksheet.get_all_records()

    existing_names = {
        row["Name"]
        for row in data
        if str(row.get("Period")) == str(period) and row.get("Subject", "").lower() == subject.lower()
    }

    copied = False
    for row in data:
        if row.get("Subject", "").lower() == subject.lower() and row["Name"] not in existing_names:
            worksheet.append_row([row["Name"], subject, period, datetime.now().strftime('%H:%M:%S')])
            copied = True

    if copied:
        print(f"[INFO] Reused attendance for '{subject}' from previous period to Period {period}.")
    else:
        print(f"[INFO] No new entries copied. All already exist for Period {period}.")
    sys.exit()


# Load faces
path = 'images'
images = []
classNames = []
for cl in os.listdir(path):
    images.append(cv2.imread(f'{path}/{cl}'))
    classNames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)
print('[INFO] Webcam Ready')

cap = cv2.VideoCapture(0)
marked_names = set()

while True:
    success, img = cap.read()
    if not success:
        break

    small_img = cv2.resize(img, (0,0), fx=0.25, fy=0.25)
    rgb_img = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)

    faces = face_recognition.face_locations(rgb_img)
    encodes = face_recognition.face_encodings(rgb_img, faces)

    for encodeFace, faceLoc in zip(encodes, faces):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        face_dist = face_recognition.face_distance(encodeListKnown, encodeFace)
        if len(face_dist) > 0:
            best = np.argmin(face_dist)
            if matches[best]:
                name = classNames[best]
                if name not in marked_names:
                    worksheet.append_row([name, subject, period, datetime.now().strftime('%H:%M:%S')])
                    marked_names.add(name)
                    print(f"[MARKED] {name} for {subject} - Period {period}")

    cv2.imshow("Attendance", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
