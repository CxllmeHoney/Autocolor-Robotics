document.addEventListener('DOMContentLoaded', function () {
    fetchData();
});

async function fetchData() {
    try {
        const response = await fetch('http://10.80.94.190:3001/api/color_data');
        const data = await response.json();

        if (response.ok) {
            displayData(data);
        } else {
            showError('เกิดข้อผิดพลาดในการโหลดข้อมูล');
        }
    } catch (error) {
        console.error('Error fetching data:', error);
        showError('เกิดข้อผิดพลาดในการโหลดข้อมูล');
    }
}

function displayData(items) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = ''; // เคลียร์ผลก่อนหน้า

    items.forEach(item => {
        const card = `
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card shadow-sm h-100">
                    <div class="card-body">
                        <h5 class="card-title">ผลการวิเคราะห์ (ID: ${item.ID})</h5>
                        <div class="color-preview" style="background-color: rgb(${item.average_color[0]}, ${item.average_color[1]}, ${item.average_color[2]}); width: 100px; height: 100px;"></div>
                        <p class="result-text"><strong>ค่าเฉลี่ยของสี (RGB):</strong> [${item.average_color}]</p>
                        <p class="result-text"><strong>ความเหมือนของสี:</strong> ${item.similarity}%</p>
                        <p class="result-text"><strong>R:</strong> ${item.red_volume} ลิตร</p>
                        <p class="result-text"><strong>G:</strong> ${item.green_volume} ลิตร</p>
                        <p class="result-text"><strong>B:</strong> ${item.blue_volume} ลิตร</p>
                        <p class="result-text"><strong>C:</strong> ${item.c_volume}</p>
                        <p class="result-text"><strong>M:</strong> ${item.m_volume}</p>
                        <p class="result-text"><strong>Y:</strong> ${item.y_volume}</p>
                        <p class="result-text"><strong>K:</strong> ${item.k_volume}</p>
                        <img src="static/uploads/${item.image}" alt="Image" class="img-fluid mt-3" />
                        <div class="button-container">
                            <a href="/details/${item.ID}" class="btn btn-primary mt-2">ไปที่หน้ารายละเอียด</a>
                        </div>
                    </div>
                </div>
            </div>`;
        resultDiv.insertAdjacentHTML('beforeend', card);
    });
    document.getElementById('loading').style.display = 'none'; // ซ่อนสปินเนอร์เมื่อโหลดเสร็จ
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block'; // แสดงข้อความผิดพลาด
    document.getElementById('loading').style.display = 'none'; // ซ่อนสปินเนอร์เมื่อเกิดข้อผิดพลาด
}
