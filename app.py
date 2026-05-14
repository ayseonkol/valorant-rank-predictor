from flask import Flask, render_template, request
import joblib
import numpy as np
import psycopg2 # sqlite3 yerine bunu kullanıyoruz
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# 1. RENDER'DAN KOPYALADIĞIN "EXTERNAL DATABASE URL"Yİ BURAYA YAPIŞTIR
DB_URL = "postgresql://valorant_db_ppak_user:Ll2ZyqgZjpcE6afzaOgAlWbYn9jRirVz@dpg-d82q81ojs32c7381d3cg-a.frankfurt-postgres.render.com/valorant_db_ppak"

# VERİTABANI BAĞLANTI FONKSİYONU
def get_db_connection():
    # Artık dosya adına değil, internetteki adrese bağlanıyoruz
    conn = psycopg2.connect(DB_URL)
    return conn

# 2. VERİTABANI BAŞLATMA FONKSİYONU (PostgreSQL Sürümü)
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # SQLite'daki 'AUTOINCREMENT' yerine PostgreSQL'de 'SERIAL' kullanılır.
    cur.execute('''CREATE TABLE IF NOT EXISTS sonuclar
                 (id SERIAL PRIMARY KEY,
                  kda FLOAT,
                  damage FLOAT,
                  headshots FLOAT,
                  assists FLOAT,
                  tahmin TEXT,
                  tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    cur.close()
    conn.close()

# Uygulama açılırken tabloyu hazırla
init_db()

# Modelleri yükleme
try:
    model = joblib.load('valorant_model.pkl')
    scaler = joblib.load('valorant_scaler.pkl')
except:
    model = None
    scaler = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        kda = float(request.form['kda'])
        damage = float(request.form['damage'])
        headshots = float(request.form['headshots'])
        assists = float(request.form['assists'])
        
        # Basit kural motoru
        if damage >= 4000 and kda >= 1.5:
            tahmin_edilen_rank = "Immortal 3"
        elif damage >= 3000 and kda >= 1.2:
            tahmin_edilen_rank = "Diamond 2"
        elif damage >= 2000 and kda >= 1.0:
            tahmin_edilen_rank = "Gold 1"
        elif damage >= 1200 and kda >= 0.8:
            tahmin_edilen_rank = "Silver 2"
        elif damage >= 500:
            tahmin_edilen_rank = "Bronze 2"
        else:
            if model and scaler:
                veriler = np.array([[kda, damage * 150, headshots * 150, assists]])
                veriler_scaled = scaler.transform(veriler)
                tahmin_edilen_rank = model.predict(veriler_scaled)[0]
            else:
                tahmin_edilen_rank = "Iron 1"
        
        # 3. VERİTABANINA KAYDETME (PostgreSQL)
        # Soru işaretleri (?) yerine %s kullanıyoruz
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO sonuclar (kda, damage, headshots, assists, tahmin) VALUES (%s, %s, %s, %s, %s)",
                  (kda, damage, headshots, assists, tahmin_edilen_rank))
        conn.commit()
        cur.close()
        conn.close()
        
        return render_template('index.html', tahmin=tahmin_edilen_rank)

# 4. YÖNETİCİ PANELİ
@app.route('/admin')
def admin():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, kda, damage, headshots, assists, tahmin, TO_CHAR(tarih, 'DD.MM.YYYY HH24:MI') FROM sonuclar ORDER BY id DESC")
    veriler = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin.html', veriler=veriler)

if __name__ == '__main__':
    app.run(debug=True)