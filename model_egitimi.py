import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
import joblib

# 1. Gerçek veri setimizi okuyoruz
try:
    df = pd.read_csv('valorant_verileri.csv', encoding='utf-8')
except:
    df = pd.read_csv('valorant_verileri.csv', encoding='latin-1')

# BÜYÜK-KÜÇÜK HARF ÇÖZÜMÜ: Tüm sütun isimlerini tamamen küçük harfe çeviriyoruz
df.columns = df.columns.str.lower()

# O garip karakterli tier sütununu düzeltmek için: içinde 'tie' geçen sütunun adını düzgünce 'tier' yapalım
for col in df.columns:
    if 'tie' in col:
        df.rename(columns={col: 'tier'}, inplace=True)

print("Sütun isimleri eşitlendi. Temizlik başlıyor...")

# 2. VERİ TEMİZLEME
for sutun in ['kills', 'deaths', 'damage', 'assists']:
    df[sutun] = df[sutun].astype(str).str.replace(',', '', regex=True)
    df[sutun] = pd.to_numeric(df[sutun], errors='coerce')

df = df.dropna(subset=['kills', 'deaths', 'damage', 'assists', 'tier'])

# 3. KDA Oranını Hesaplama
df['deaths'] = df['deaths'].replace(0, 1)
df['kda_orani'] = df['kills'] / df['deaths']

# 4. Özellikleri (X) ve Hedefi (y) Seçme
X = df[['kda_orani', 'damage', 'headshots', 'assists']]
y = df['tier']

# 5. Veriyi Ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Veri Ölçeklendirme
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 7. KNN Modelini Eğitme
print("Yapay zeka modeli harf hassasiyeti düzeltilerek yeniden eğitiliyor...")
model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train_scaled, y_train)

# Başarı Oranını Görme
basari = model.score(X_test_scaled, y_test)
print("-" * 40)
print(f"Model Başarıyla Güncellendi!")
print(f"Yeni Başarı Oranı: %{basari * 100:.2f}")
print("-" * 40)

# 8. Yeni Modelleri Kaydetme
joblib.dump(model, 'valorant_model.pkl')
joblib.dump(scaler, 'valorant_scaler.pkl')
print("Akıllı pkl dosyaları başarıyla güncellendi.")