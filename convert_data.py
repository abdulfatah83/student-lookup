
import pandas as pd
import json
import sqlite3
import os
import sys

# ضبط الترميز للطباعة
sys.stdout.reconfigure(encoding='utf-8')

# قراءة ملف Excel
print("Reading Excel file...")
try:
    df = pd.read_excel('data.xlsx')
except Exception as e:
    print(f"Error reading Excel file: {e}")
    sys.exit(1)

# تحويل البيانات إلى قائمة من القواميس
students_list = []
for _, row in df.iterrows():
    # التعامل مع القيم الفارغة
    if pd.isna(row['رقم القيد']):
        continue
        
    student = {
        'name': str(row['اسم الطالب']).strip(),
        'registrationNumber': str(int(row['رقم القيد'])),
        'seatNumber': str(int(row['رقم الجلوس'])),
        'academicYear': str(row['السنة الدراسية']).strip(),
        'examHall': str(row['القاعة الإمتحانية ']).strip()
    }
    students_list.append(student)

# حفظ البيانات في ملف JSON
print("Saving to JSON...")
with open('students_data.json', 'w', encoding='utf-8') as f:
    json.dump(students_list, f, ensure_ascii=False, indent=2)

# تحديث قاعدة البيانات
print("Updating SQLite database...")
try:
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    # حذف الجدول القديم لإعادة إنشائه
    cursor.execute('DROP TABLE IF EXISTS students')

    # إنشاء جدول الطلبة
    cursor.execute('''
    CREATE TABLE students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        registration_number TEXT UNIQUE NOT NULL,
        seat_number TEXT NOT NULL,
        academic_year TEXT NOT NULL,
        exam_hall TEXT NOT NULL
    )
    ''')

    # إنشاء index للبحث السريع
    cursor.execute('''
    CREATE INDEX idx_registration 
    ON students(registration_number)
    ''')

    # إدخال البيانات
    count = 0
    for student in students_list:
        try:
            cursor.execute('''
            INSERT INTO students (name, registration_number, seat_number, academic_year, exam_hall)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                student['name'],
                student['registrationNumber'],
                student['seatNumber'],
                student['academicYear'],
                student['examHall']
            ))
            count += 1
        except sqlite3.IntegrityError:
            print(f"Warning: Duplicate registration number skipped: {student['registrationNumber']}")

    conn.commit()
    conn.close()

    print(f"تم تحديث قاعدة البيانات بنجاح. تم إدراج {count} طالب.")

except Exception as e:
    print(f"Error updating database: {e}")
