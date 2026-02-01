from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import json
import os

app = Flask(__name__, static_folder='.')
CORS(app)  # السماح بالطلبات من أي مصدر

def init_database():
    """إنشاء قاعدة البيانات وتعبئتها تلقائياً"""
    if not os.path.exists('students.db'):
        print("Creating database...")
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
        
        # استيراد البيانات من JSON
        if os.path.exists('students_data.json'):
            with open('students_data.json', 'r', encoding='utf-8') as f:
                students = json.load(f)
            
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
            print(f"Database created with {count} students")
        
        conn.close()

def get_db_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

# تهيئة قاعدة البيانات عند بدء التطبيق
init_database()

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """ملفات CSS, JS, وغيرها"""
    return send_from_directory('.', path)

@app.route('/api/search', methods=['GET'])
def search_student():
    """البحث عن طالب برقم القيد"""
    registration_number = request.args.get('registration_number', '').strip()
    
    if not registration_number:
        return jsonify({
            'success': False,
            'message': 'رقم القيد مطلوب'
        }), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT name, registration_number, seat_number, academic_year, exam_hall
        FROM students
        WHERE registration_number = ?
        ''', (registration_number,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'success': True,
                'student': {
                    'name': result['name'],
                    'registrationNumber': result['registration_number'],
                    'seatNumber': result['seat_number'],
                    'academicYear': result['academic_year'],
                    'examHall': result['exam_hall']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'الطالب غير موجود'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في الخادم: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """فحص حالة الخادم"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        count = cursor.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'students_count': count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting server...")
    print("Server available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
