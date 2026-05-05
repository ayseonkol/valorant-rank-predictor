from flask import Flask, render_template, request
import joblib
import numpy as np

app = Flask(__name__)

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
        # Kullanıcının girdiği 1 maçlık normal verileri alıyoruz
        kda = float(request.form['kda'])
        damage = float(request.form['damage'])
        headshots = float(request.form['headshots'])
        assists = float(request.form['assists'])
        
        # 💡 TEK MAÇLIK KURAL MOTORU (Kullanıcı Dostu Çözüm)
        # Kullanıcı tamamen tek maçlık skorlar girdiğinde çalışacak net sınırlar:
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
            # Değerler gerçekten çok düşükse model ne diyorsa o (Muhtemelen Iron)
            if model and scaler:
                veriler = np.array([[kda, damage * 150, headshots * 150, assists]])
                veriler_scaled = scaler.transform(veriler)
                tahmin_edilen_rank = model.predict(veriler_scaled)[0]
            else:
                tahmin_edilen_rank = "Iron 1"
        
        return render_template('index.html', tahmin=tahmin_edilen_rank)

if __name__ == '__main__':
    app.run(debug=True)