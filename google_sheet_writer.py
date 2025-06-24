#HEY THIS IS OPTIONAL I ALREADY INTEGRATED THIS CODE IN THE face_attendance.py file so make sure about it #
#google_Sheet_writer.py
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from datetime import datetime

# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
# client = gspread.authorize(creds)

# SHEET_NAME = "Face_Attendance"

# def has_existing_attendance(subject, date_str):
#     try:
#         sheet = client.open(SHEET_NAME)
#         worksheet = sheet.worksheet(date_str)
#         records = worksheet.get_all_records()
#         return any(row.get("Subject", "").lower() == subject.lower() for row in records)
#     except:
#         return False

# def copy_attendance_if_exists(prev_period, curr_period, subject, date_str):
#     sheet = client.open(SHEET_NAME)
#     try:
#         worksheet = sheet.worksheet(date_str)
#     except:
#         worksheet = sheet.add_worksheet(title=date_str, rows="1000", cols="4")
#         worksheet.append_row(["Name", "Subject", "Period", "Time"])

#     records = worksheet.get_all_records()

#     # 🛡️ Avoid duplicate copying
#     existing_names = {
#         row["Name"]
#         for row in records
#         if str(row.get("Period")) == str(curr_period) and row.get("Subject", "").lower() == subject.lower()
#     }

#     copied = False
#     for row in records:
#         if str(row.get("Period")) == str(prev_period) and row.get("Subject", "").lower() == subject.lower():
#             if row["Name"] not in existing_names:
#                 worksheet.append_row([
#                     row["Name"], subject, curr_period, datetime.now().strftime('%H:%M:%S')
#                 ])
#                 copied = True

#     if copied:
#         print(f"[INFO] Attendance copied from Period {prev_period} for subject '{subject}'.")
#     else:
#         print(f"[INFO] No new names copied — all entries already exist for Period {curr_period}.")


# def mark_attendance(name, subject, period):
#     now = datetime.now()
#     date_str = now.strftime('%Y-%m-%d')
#     time_str = now.strftime('%H:%M:%S')

#     sheet = client.open(SHEET_NAME)
#     try:
#         worksheet = sheet.worksheet(date_str)
#     except:
#         worksheet = sheet.add_worksheet(title=date_str, rows="1000", cols="4")
#         worksheet.append_row(["Name", "Subject", "Period", "Time"])

#     records = worksheet.get_all_records()

#     if len(records) == 0:
#         worksheet.append_row(["Name", "Subject", "Period", "Time"])

#     for row in records:
#         if row["Name"] == name and str(row["Period"]) == str(period) and row["Subject"].lower() == subject.lower():
#             print(f"[INFO] Already marked: {name} for {subject} - Period {period}")
#             return

#     worksheet.append_row([name, subject, period, time_str])
#     print(f"[SUCCESS] Marked {name} for {subject} - Period {period} at {time_str}")

