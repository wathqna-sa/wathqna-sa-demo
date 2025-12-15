from flask import Flask, request
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    'file': {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'},
    'audio': {'mp3', 'wav'},
    'video': {'mp4'}
}

def allowed_file(filename, category):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[category]

def render_page(content, step_num=1, success=False):
    popup_script = """
    <script>
        window.onload = function() {
            alert("🎉 تم توثيق فكرتك بنجاح!");
        }
    </script>
    """ if success else ""

    return f"""
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>منصة وَثَّقْنَا</title>
        <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        {popup_script}
        <style>
            body {{
                background-color: #f0f8f5;
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .navbar {{
                background-color: #2e7d32;
                padding: 15px 30px;
                color: white;
                font-size: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .container {{
                max-width: 750px;
                margin: 30px auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 0 15px rgba(0,0,0,0.1);
                padding: 30px;
            }}
            h2, h3 {{
                color: #2e7d32;
            }}
            label {{
                font-weight: bold;
                display: block;
                margin-top: 15px;
            }}
            input[type='text'], textarea, input[type='file'] {{
                width: 100%;
                padding: 10px;
                margin-top: 5px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
            }}
            input[type='submit'], .print-btn {{
                background-color: #2e7d32;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                margin-top: 20px;
                cursor: pointer;
                font-size: 16px;
            }}
            input[type='submit']:hover, .print-btn:hover {{
                background-color: #1b5e20;
            }}
            .note {{
                font-size: 0.9em;
                color: #888;
            }}
            a {{
                display: inline-block;
                margin-top: 20px;
                text-decoration: none;
                color: #2e7d32;
            }}
            .step-header {{
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }}
            .step {{
                padding: 6px 12px;
                border-radius: 20px;
                background-color: #e8f5e9;
                color: #2e7d32;
                font-weight: bold;
                font-size: 14px;
            }}
            .step.active {{
                background-color: #2e7d32;
                color: white;
            }}
            .icon {{
                margin-left: 8px;
                color: #2e7d32;
            }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <span>📄</span> منصة وَثَّقْنَا
        </div>
        <div class="container">
            <div class="step-header">
                <div class="step {'active' if step_num == 1 else ''}">١. الدخول</div>
                <div class="step {'active' if step_num == 2 else ''}">٢. التفاصيل</div>
                <div class="step {'active' if step_num == 3 else ''}">٣. الملفات</div>
                <div class="step {'active' if step_num == 4 else ''}">٤. التأكيد</div>
            </div>
            {content}
        </div>
    </body>
    </html>
    """

@app.route('/')
def login():
    return render_page("""
        <h2><i class="fas fa-sign-in-alt icon"></i> تسجيل الدخول</h2>
        <form action='/dashboard' method='post'>
            <label><i class="fas fa-id-card icon"></i> رقم الهوية / الدخول عبر نفاذ:</label>
            <input type='text' name='user' required>
            <input type='submit' value='دخول'>
        </form>
    """, step_num=1)

@app.route('/dashboard', methods=['POST'])
def dashboard():
    return render_page("""
        <h3><i class="fas fa-lightbulb icon"></i> تفاصيل الفكرة</h3>
        <form action='/submit' method='post' enctype='multipart/form-data'>
            <label><i class="fas fa-heading icon"></i> عنوان الفكرة:</label>
            <input type='text' name='title' required>

            <label><i class="fas fa-align-left icon"></i> وصف الفكرة:</label>
            <textarea name='description' rows="4" required></textarea>

            <label><i class="fas fa-file-upload icon"></i> ملف وصفي:</label>
            <input type='file' name='file' accept=".pdf,.doc,.docx,.png,.jpg,.jpeg">

            <label><i class="fas fa-microphone icon"></i> تسجيل صوتي:</label>
            <input type='file' name='audio' accept=".mp3,.wav">

            <label><i class="fas fa-video icon"></i> فيديو وصفي:</label>
            <input type='file' name='video' accept=".mp4">

            <input type='checkbox' name='agreement' required> أقرّ أنني أتحمل كامل المسؤولية عن هذه الفكرة.<br><br>

            <input type='submit' value='توثيق الفكرة'>
        </form>
    """, step_num=2)

@app.route('/submit', methods=['POST'])
def submit():
    title = request.form['title']
    description = request.form['description']
    agreement = request.form.get('agreement')
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if not agreement:
        return render_page("<h3>⚠️ يجب الموافقة على الشروط قبل توثيق الفكرة.</h3>", step_num=3)

    uploads = []
    for field in ['file', 'audio', 'video']:
        file = request.files.get(field)
        if file and file.filename:
            if allowed_file(file.filename, field):
                filename = secure_filename(f"{timestamp}_{field}_{file.filename}")
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                uploads.append(filename)
            else:
                return render_page(f"<h3>🚫 نوع الملف غير مسموح به في الحقل: <strong>{field}</strong></h3>", step_num=3)

    registration_number = f"WTQ-{timestamp.replace('-', '').replace(':', '').replace('_', '')[:12]}"

    with open(os.path.join(UPLOAD_FOLDER, f"{timestamp}_meta.txt"), 'w', encoding='utf-8') as f:
        f.write(f"عنوان: {title}\nوصف: {description}\nوقت: {timestamp}\nرقم التسجيل: {registration_number}\n")

    return render_page(f"""
        <h2><i class="fas fa-check-circle icon"></i> تم توثيق فكرتك</h2>
        <p><strong>العنوان:</strong> {title}</p>
        <p><strong>الوصف:</strong> {description}</p>
        <p><strong>الوقت:</strong> {timestamp}</p>
        <p><strong>رقم التسجيل:</strong> {registration_number}</p>
        <p class='note'>✅ تم إرسال تأكيد إلى بريدك وهاتفك.</p>
        <button class="print-btn" onclick="window.print()"><i class="fas fa-print icon"></i> طباعة</button><br>
        <a href='/'><i class="fas fa-arrow-left icon"></i> العودة للرئيسية</a>
    """, step_num=4, success=True)

# أهم سطر لتشغيله على Replit
app.run(host='0.0.0.0', port=81)
