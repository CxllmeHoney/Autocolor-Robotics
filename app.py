from flask import Flask, render_template, request, redirect, url_for, session, flash
from PIL import Image
import numpy as np
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # ใช้สำหรับ session

# กำหนดโฟลเดอร์สำหรับจัดเก็บไฟล์
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ตัวอย่างข้อมูลผู้ใช้
users = {'user1': 'password1', 'user2': 'password2'}

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Username หรือ Password ไม่ถูกต้อง')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if username in users:
            flash('Username นี้มีผู้ใช้งานแล้ว')
        elif password != confirm_password:
            flash('รหัสผ่านไม่ตรงกัน')
        else:
            users[username] = password
            flash('ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    total_volume = float(request.form['volume'])  # รับค่าปริมาตรสีจากผู้ใช้

    if file.filename == '':
        return redirect(request.url)

    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # ประมวลผลภาพ
        average_color, similarity, red_ratio, green_ratio, blue_ratio, red_volume, green_volume, blue_volume, c, m, y, k, c_volume, m_volume, y_volume, k_volume = process_image(filepath, total_volume)

        return render_template('results.html',
                               average_color=average_color,
                               similarity=similarity,
                               red_ratio=red_ratio,
                               green_ratio=green_ratio,
                               blue_ratio=blue_ratio,
                               red_volume=red_volume,
                               green_volume=green_volume,
                               blue_volume=blue_volume,
                               c=c, m=m, y=y, k=k,
                               c_volume=c_volume,
                               m_volume=m_volume,
                               y_volume=y_volume,
                               k_volume=k_volume,
                               output_folder=OUTPUT_FOLDER,
                               file_name=file.filename)
    return redirect(url_for('index'))

def calculate_average_color(image_path):
    image = Image.open(image_path)
    image = image.convert('RGB')
    image_np = np.array(image)
    average_color = np.mean(image_np, axis=(0, 1)).astype(int)
    return average_color

def create_average_color_image(average_color, image_size=(100, 100)):
    average_color_image = Image.new("RGB", image_size, tuple(average_color))
    return average_color_image

def calculate_color_similarity(original_image_path, average_color):
    image = Image.open(original_image_path)
    image = image.convert('RGB')
    image_np = np.array(image)
    diff = np.linalg.norm(image_np - average_color, axis=2)
    max_diff = np.linalg.norm([255, 255, 255])
    similarity = (1 - np.mean(diff) / max_diff) * 100
    return similarity

def calculate_color_ratio(image_path):
    image = Image.open(image_path)
    image = image.convert('RGB')
    image_np = np.array(image)
    total_pixels = image_np.shape[0] * image_np.shape[1]
    red_ratio = np.sum(image_np[:, :, 0]) / (255 * total_pixels)
    green_ratio = np.sum(image_np[:, :, 1]) / (255 * total_pixels)
    blue_ratio = np.sum(image_np[:, :, 2]) / (255 * total_pixels)
    return red_ratio, green_ratio, blue_ratio

def calculate_real_world_ratios(red_ratio, green_ratio, blue_ratio):
    total_ratio = red_ratio + green_ratio + blue_ratio
    red_real_world_ratio = red_ratio / total_ratio
    green_real_world_ratio = green_ratio / total_ratio
    blue_real_world_ratio = blue_ratio / total_ratio
    return red_real_world_ratio, green_real_world_ratio, blue_real_world_ratio

def calculate_paint_mix_volume(total_volume, red_ratio, green_ratio, blue_ratio):
    red_volume = total_volume * red_ratio
    green_volume = total_volume * green_ratio
    blue_volume = total_volume * blue_ratio
    return red_volume, green_volume, blue_volume

def rgb_to_cmyk(r, g, b):
    r_ratio = r / 255
    g_ratio = g / 255
    b_ratio = b / 255
    
    k = 1 - max(r_ratio, g_ratio, b_ratio)
    if k == 1:
        return 0, 0, 0, 1  # black only

    c = (1 - r_ratio - k) / (1 - k)
    m = (1 - g_ratio - k) / (1 - k)
    y = (1 - b_ratio - k) / (1 - k)
    
    return c, m, y, k

def calculate_cmyk_volume(total_volume, c, m, y, k):
    c_volume = total_volume * c
    m_volume = total_volume * m
    y_volume = total_volume * y
    k_volume = total_volume * k
    return c_volume, m_volume, y_volume, k_volume

def process_image(filepath, total_volume):
    # RGB calculations
    average_color = calculate_average_color(filepath)
    red_ratio, green_ratio, blue_ratio = calculate_color_ratio(filepath)
    red_real_world_ratio, green_real_world_ratio, blue_real_world_ratio = calculate_real_world_ratios(red_ratio, green_ratio, blue_ratio)
    red_volume, green_volume, blue_volume = calculate_paint_mix_volume(total_volume, red_real_world_ratio, green_real_world_ratio, blue_real_world_ratio)

    # CMYK calculations
    c, m, y, k = rgb_to_cmyk(average_color[0], average_color[1], average_color[2])
    c_volume, m_volume, y_volume, k_volume = calculate_cmyk_volume(total_volume, c, m, y, k)

    similarity = calculate_color_similarity(filepath, average_color)

    # Save average color image
    average_color_image = create_average_color_image(average_color)
    average_color_image_path = os.path.join(OUTPUT_FOLDER, 'average_color_image.jpg')
    average_color_image.save(average_color_image_path)

    return average_color, similarity, red_ratio, green_ratio, blue_ratio, red_volume, green_volume, blue_volume, c, m, y, k, c_volume, m_volume, y_volume, k_volume

if __name__ == '__main__':
    app.run(debug=True)
