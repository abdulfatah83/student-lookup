// Basic Setup
const API_BASE_URL = window.location.origin;

// DOM Elements
const searchPage = document.getElementById('searchPage');
const resultPage = document.getElementById('resultPage');

const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const backBtn = document.getElementById('backBtn');
const printBtn = document.getElementById('printBtn');

const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

// Result Fields
const resName = document.getElementById('resName');
const resRegNum = document.getElementById('resRegNum');
const resAcademicYear = document.getElementById('resAcademicYear');
const resSeatNum = document.getElementById('resSeatNum');
const resHall = document.getElementById('resHall');
const refId = document.getElementById('refId');
const docYear = document.getElementById('docYear');
const printDate = document.getElementById('printDate'); // If exists in hidden header

// Event Listeners
searchBtn.addEventListener('click', performSearch);
backBtn.addEventListener('click', showSearchPage);
printBtn.addEventListener('click', () => window.print());

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
});

searchInput.addEventListener('input', () => {
    // Hide error when typing
    errorMessage.style.display = 'none';
});

// Functions
async function performSearch() {
    const query = searchInput.value.trim();

    if (!query) {
        showError('الرجاء إدخال رقم القيد');
        return;
    }

    showLoading(true);
    errorMessage.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE_URL}/api/search?registration_number=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (response.ok && data.success) {
            displayResult(data.student);
        } else {
            showError('رقم القيد غير موجود في المنظومة. تأكد من الرقم وحاول مجدداً.');
        }
    } catch (error) {
        console.error(error);
        showError('خطأ في الاتصال بالخادم.');
    } finally {
        showLoading(false);
    }
}

function displayResult(student) {
    // Populate Data
    resName.textContent = student.name;
    resRegNum.textContent = student.registrationNumber; // Using JSON keys from API
    resAcademicYear.textContent = student.academicYear;
    resSeatNum.textContent = student.seatNumber;
    resHall.textContent = student.examHall;

    // Generate a random Reference ID for the "official" look
    refId.textContent = `STD-${Date.now().toString().slice(-6)}-${Math.floor(Math.random() * 1000)}`;

    // Switch View
    searchPage.style.display = 'none';
    resultPage.style.display = 'block';

    // Scroll to top
    window.scrollTo(0, 0);
}

function showSearchPage() {
    resultPage.style.display = 'none';
    searchPage.style.display = 'block'; // Or flex/whatever logic
    searchPage.classList.add('active'); // Ensure animation if any

    searchInput.value = '';
    searchInput.focus();
    errorMessage.style.display = 'none';
}

function showLoading(isLoading) {
    if (isLoading) {
        searchBtn.disabled = true;
        loadingIndicator.style.display = 'flex';
        searchBtn.style.opacity = '0.7';
    } else {
        searchBtn.disabled = false;
        loadingIndicator.style.display = 'none';
        searchBtn.style.opacity = '1';
    }
}

function showError(msg) {
    errorText.textContent = msg;
    errorMessage.style.display = 'flex';

    // Shake effect
    const box = document.querySelector('.search-box');
    box.classList.add('shake-animation'); // You'd need CSS for this or just rely on the existing shake on error msg
}
