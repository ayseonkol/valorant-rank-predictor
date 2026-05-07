from flask import Flask, render_template, request
import joblib
import numpy as np
import sqlite3

app = Flask(__name__)

# 1. VERİTABANI BAŞLATMA
def init_db():
    conn = sqlite3.connect('tahminler.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sonuclar
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  kda REAL,
                  damage REAL,
                  headshots REAL,
                  assists REAL,
                  tahmin TEXT,
                  tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

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
        
        # Tek maçlık kural motoru
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
        
        # 2. VERİTABANINA KAYIT
        conn = sqlite3.connect('tahminler.db')
        c = conn.cursor()
        c.execute("INSERT INTO sonuclar (kda, damage, headshots, assists, tahmin) VALUES (?, ?, ?, ?, ?)",
                  (kda, damage, headshots, assists, tahmin_edilen_rank))
        conn.commit()
        conn.close()
        
        return render_template('index.html', tahmin=tahmin_edilen_rank)

# 3. YÖNETİCİ PANELİ (GİZLİ SAYFA)
@app.route('/admin')
def admin():
    conn = sqlite3.connect('tahminler.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sonuclar ORDER BY id DESC")
    veriler = c.fetchall()
    conn.close()
    return render_template('admin.html', veriler=veriler)

if __name__ == '__main__':
    app.run(debug=True)
