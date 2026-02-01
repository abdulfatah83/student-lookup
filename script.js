// متغيرات عامة
// تحديد رابط API - سيتم استخدامه في الإنتاج أيضاً
const API_BASE_URL = window.location.origin; // يستخدم نفس المصدر

// العناصر من DOM
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const clearBtn = document.getElementById('clearBtn');
const resultSection = document.getElementById('resultSection');
const notFoundSection = document.getElementById('notFoundSection');
const loadingSection = document.getElementById('loadingSection');

// لا حاجة لتحميل البيانات مسبقاً - سنستخدم API مباشرة

// إظهار/إخفاء زر المسح
searchInput.addEventListener('input', () => {
    if (searchInput.value.trim()) {
        clearBtn.style.display = 'flex';
    } else {
        clearBtn.style.display = 'none';
    }
});

// مسح حقل البحث
clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    clearBtn.style.display = 'none';
    hideAllSections();
    searchInput.focus();
});

// البحث بالضغط على Enter
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

// البحث بالنقر على الزر
searchBtn.addEventListener('click', performSearch);

// وظيفة البحث الرئيسية
async function performSearch() {
    const registrationNumber = searchInput.value.trim();

    // التحقق من إدخال رقم القيد
    if (!registrationNumber) {
        searchInput.focus();
        searchInput.classList.add('shake');
        setTimeout(() => searchInput.classList.remove('shake'), 500);
        return;
    }

    // إظهار رسالة التحميل
    showLoading();

    try {
        // استدعاء API
        const response = await fetch(`${API_BASE_URL}/api/search?registration_number=${encodeURIComponent(registrationNumber)}`);
        const data = await response.json();

        if (response.ok && data.success) {
            // تم العثور على الطالب
            displayResult(data.student);
        } else {
            // الطالب غير موجود
            displayNotFound();
        }
    } catch (error) {
        console.error('خطأ في البحث:', error);
        hideAllSections();
        alert('حدث خطأ في الاتصال بالخادم. يرجى المحاولة مرة أخرى.');
    }
}

// عرض النتائج
function displayResult(student) {
    hideAllSections();

    const resultHTML = `
        <div class="result-card" id="studentCard" dir="rtl">
            <!-- رأس الجامعة في البطاقة -->
            <div class="card-university-header">
                <div class="card-university-logo">🎓</div>
                <div class="card-university-name">جامعة المرقب</div>
                <div class="card-faculty-name">كلية العلوم الصحية - قسم المختبرات الطبية</div>
            </div>
            
            <div class="card-divider"></div>
            
            <div class="result-header">
                <div class="result-icon">✓</div>
                <div class="result-title">
                    <h2>بطاقة معلومات الجلوس</h2>
                    <p>معلومات الطالب</p>
                </div>
            </div>
            
            <div class="result-details">
                <div class="detail-item">
                    <div class="detail-content">
                        <div class="detail-label">اسم الطالب</div>
                        <div class="detail-value">${student.name}</div>
                    </div>
                    <div class="detail-icon">👤</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-content">
                        <div class="detail-label">رقم القيد</div>
                        <div class="detail-value">${student.registrationNumber}</div>
                    </div>
                    <div class="detail-icon">🎫</div>
                </div>
                
                <div class="detail-item highlight">
                    <div class="detail-content">
                        <div class="detail-label">رقم الجلوس</div>
                        <div class="detail-value">${student.seatNumber}</div>
                    </div>
                    <div class="detail-icon">💺</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-content">
                        <div class="detail-label">السنة الدراسية</div>
                        <div class="detail-value">${student.academicYear}</div>
                    </div>
                    <div class="detail-icon">📚</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-content">
                        <div class="detail-label">القاعة الامتحانية</div>
                        <div class="detail-value">${student.examHall}</div>
                    </div>
                    <div class="detail-icon">🏛️</div>
                </div>
            </div>
            
            <div class="card-footer">
                <div class="approval-section">
                    <div class="approval-label">اعتماد رئيس القسم</div>
                    <div class="signature-line"></div>
                </div>
            </div>
        </div>
        
        <button class="print-btn" id="printBtn">
            <span>📥</span>
            <span>تحميل البطاقة كصورة</span>
        </button>
    `;

    resultSection.innerHTML = resultHTML;
    resultSection.style.display = 'block';

    // إضافة حدث الطباعة
    const printBtn = document.getElementById('printBtn');
    if (printBtn) {
        printBtn.addEventListener('click', downloadCardAsImage);
    }

    // تأثير صوت النجاح (اختياري)
    playSuccessAnimation();
}

// تحميل البطاقة كصورة
async function downloadCardAsImage() {
    const card = document.getElementById('studentCard');
    const printBtn = document.getElementById('printBtn');

    if (!card) return;

    try {
        // تغيير نص الزر أثناء المعالجة
        const originalHTML = printBtn.innerHTML;
        printBtn.innerHTML = '<span>⏳</span><span>جاري التحميل...</span>';
        printBtn.disabled = true;

        // إنشاء نسخة من البطاقة للطباعة
        const canvas = await html2canvas(card, {
            backgroundColor: '#1a1a35',
            scale: 2, // جودة عالية
            logging: false,
            useCORS: true
        });

        // تحويل إلى صورة وتحميلها
        canvas.toBlob(function (blob) {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            const registrationNumber = card.querySelector('.detail-value').textContent || 'student';
            link.download = `بطاقة_جلوس_${Date.now()}.png`;
            link.href = url;
            link.click();
            URL.revokeObjectURL(url);

            // إعادة الزر لحالته الأصلية
            printBtn.innerHTML = originalHTML;
            printBtn.disabled = false;
        });

    } catch (error) {
        console.error('خطأ في تحميل البطاقة:', error);
        alert('حدث خطأ في تحميل البطاقة. يرجى المحاولة مرة أخرى.');
        printBtn.innerHTML = '<span>📥</span><span>تحميل البطاقة كصورة</span>';
        printBtn.disabled = false;
    }
}

// عرض رسالة عدم العثور
function displayNotFound() {
    hideAllSections();
    notFoundSection.style.display = 'block';
}

// إظهار رسالة التحميل
function showLoading() {
    hideAllSections();
    loadingSection.style.display = 'block';
}

// إخفاء جميع الأقسام
function hideAllSections() {
    resultSection.style.display = 'none';
    notFoundSection.style.display = 'none';
    loadingSection.style.display = 'none';
}

// تأثير النجاح
function playSuccessAnimation() {
    const resultCard = document.querySelector('.result-card');
    if (resultCard) {
        resultCard.style.animation = 'none';
        setTimeout(() => {
            resultCard.style.animation = 'fadeInScale 0.5s ease-out';
        }, 10);
    }
}

// تأثير اهتزاز لحقل البحث عند الخطأ
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    .shake {
        animation: shake 0.3s ease-in-out;
    }
`;
document.head.appendChild(style);
