import pandas as pd

# 1. Klasördeki CSV dosyamızı okuyoruz
df = pd.read_csv('valorant_verileri.csv')

# 2. Tablonun ilk 5 satırını ekrana yazdıralım ki doğru okumuş mu görelim
print("--- VERİ SETİNİN İLK 5 SATIRI ---")
print(df.head())
print("\n")

# 3. Hangi rütbeden (tier) kaç tane oyuncu verisi var, sayalım
print("--- RÜTBELERE (TIER) GÖRE OYUNCU SAYISI ---")
print(df['tier'].value_counts())