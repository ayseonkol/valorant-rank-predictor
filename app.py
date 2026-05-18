import os
import sqlite3
import psycopg2
from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)

# Modeli yükle
model = joblib.load("hantavirus_modeli.pkl")


# 1. VERİTABANI BAĞLANTI FONKSİYONU
def get_db_connection():
    # Eğer Render üzerindeysek DATABASE_URL çevresel değişkeni otomatik dolu olur
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        # RENDER / POSTGRESQL BAĞLANTISI
        conn = psycopg2.connect(db_url)
    else:
        # BİLGİSAYARINIZ / SQLITE BAĞLANTISI
        conn = sqlite3.connect('hantavirus_sonuclar.db')
        
    return conn


# 2. TABLO OLUŞTURMA FONKSİYONU
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Kodun nerede çalıştığına göre ID yapısını ayarlıyoruz (Hatasız çalışması için)
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        id_text = "id SERIAL PRIMARY KEY"
    else:
        id_text = "id INTEGER PRIMARY KEY AUTOINCREMENT"
        
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS tahminler (
            {id_text},
            yas INTEGER,
            cinsiyet TEXT,
            semptom_sayisi INTEGER,
            sonuc TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Uygulama her başladığında veritabanı tablosunu hazırla
init_db()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Form verilerini al
        age = int(request.form['Age'])
        gender = request.form['Gender']
        symptoms_list = request.form.getlist('symptoms')
        symptom_count = len(symptoms_list)
        gender_m = 1 if gender == 'M' else 0

        # Model için veri çerçevesi oluştur
        input_data = pd.DataFrame([[age, symptom_count, gender_m]], 
                                  columns=['Age', 'Symptom_Count', 'Gender_M'])

        # Modelden tahmin al
        prediction = model.predict(input_data)

        # 3 altı/4 üstü kuralın ve sonuç metinlerin
        if symptom_count <= 3:
            result = "Hantavirüs NEGATİF (Düşük Risk)" 
        else:
            result = "Hantavirüs POZİTİF (Yüksek Risk)"

        prediction_text = f'Tahmin Sonucu: {result}'

        if gender == 'M':
            cinsiyet_turkce = "Erkek"
        elif gender == 'F':
            cinsiyet_turkce = "Kadın"
        else:
            cinsiyet_turkce = gender


        # 3. VERİTABANINA KAYDETME
        conn = get_db_connection()
        cursor = conn.cursor()
        
        db_url = os.environ.get('DATABASE_URL')
        if db_url:
            # Render/PostgreSQL için sorgu kalıbı
            query = "INSERT INTO tahminler (yas, cinsiyet, semptom_sayisi, sonuc) VALUES (%s, %s, %s, %s)"
        else:
            # Bilgisayar/SQLite için sorgu kalıbı
            query = "INSERT INTO tahminler (yas, cinsiyet, semptom_sayisi, sonuc) VALUES (?, ?, ?, ?)"
            
        cursor.execute(query, (age, cinsiyet_turkce, symptom_count, prediction_text))
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✓ Veri tabanına başarıyla kaydedildi!")

    except Exception as e:
        print("X Veri tabanı işlemi sırasında hata oluştu:", e)
        # Eğer bir hata olursa formun çökmemesi için yedek mesaj
        prediction_text = "Sistemde bir hata oluştu, lütfen tekrar deneyin."

    return render_template('index.html', prediction_text=prediction_text)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)