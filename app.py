from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder='.')
CORS(app)  # السماح بالطلبات من أي مصدر

def get_db_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

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
    # التأكد من وجود قاعدة البيانات
    if not os.path.exists('students.db'):
        print("⚠️ قاعدة البيانات غير موجودة. قم بتشغيل database.py أولاً")
        print("python database.py")
        exit(1)
    
    print("🚀 بدء تشغيل الخادم...")
    print("📍 الموقع متاح على: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
