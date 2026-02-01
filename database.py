import sqlite3
import json
import os
import sys

# ضبط الترميز للطباعة
sys.stdout.reconfigure(encoding='utf-8')

def create_database():
    """إنشاء قاعدة البيانات والجدول"""
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # إنشاء جدول الطلبة
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
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
    CREATE INDEX IF NOT EXISTS idx_registration 
    ON students(registration_number)
    ''')
    
    conn.commit()
    conn.close()
    print("تم إنشاء قاعدة البيانات بنجاح")

def import_data_from_json():
    """استيراد البيانات من ملف JSON إلى قاعدة البيانات"""
    if not os.path.exists('students_data.json'):
        print("ملف students_data.json غير موجود")
        return
    
    # قراءة البيانات من JSON
    with open('students_data.json', 'r', encoding='utf-8') as f:
        students = json.load(f)
    
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # حذف البيانات القديمة إن وجدت
    cursor.execute('DELETE FROM students')
    
    # إدخال البيانات
    for student in students:
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
    
    conn.commit()
    count = cursor.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    conn.close()
    
    print(f"تم استيراد {count} طالب إلى قاعدة البيانات")

def search_student(registration_number):
    """البحث عن طالب برقم القيد"""
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT name, registration_number, seat_number, academic_year, exam_hall
    FROM students
    WHERE registration_number = ?
    ''', (registration_number,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'name': result[0],
            'registrationNumber': result[1],
            'seatNumber': result[2],
            'academicYear': result[3],
            'examHall': result[4]
        }
    return None

if __name__ == '__main__':
    print("إعداد قاعدة البيانات...")
    create_database()
    import_data_from_json()
    
    # اختبار البحث
    print("\nاختبار البحث...")
    test_student = search_student('222031353')
    if test_student:
        print(f"تم العثور على: {test_student['name']}")
    else:
        print("لم يتم العثور على الطالب")
