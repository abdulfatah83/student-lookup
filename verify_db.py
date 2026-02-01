

import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')


try:
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # Check count
    count = cursor.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    print(f"Total students: {count}")
    
    # Check specific student
    reg_num = "222031353"
    student = cursor.execute('SELECT * FROM students WHERE registration_number = ?', (reg_num,)).fetchone()
    
    if student:
        print(f"Found student: {student[1]}")
    else:
        print("Student not found")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
