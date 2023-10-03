import random
import tkinter as tk
from tkinter import messagebox
import sqlite3

sorular = []
cevaplar = []

# Veritabanı bağlantısı oluştur
baglanti = sqlite3.connect("soru_cevap_veritabani.db")
cursor = baglanti.cursor()

# Eğer "dogru_cevaplar" adında bir tablo yoksa oluştur
cursor.execute('''CREATE TABLE IF NOT EXISTS dogru_cevaplar
                  (soru TEXT, cevap TEXT)''')
baglanti.commit()

# Soruları ve cevapları dosyalardan oku
with open('sorular.txt', 'r', encoding='utf-8') as sorular_dosya:
    sorular = sorular_dosya.read().splitlines()

# Cevapları dosyadan oku
with open('cevaplar.txt', 'r', encoding='utf-8') as cevaplar_dosya:
    cevaplar = cevaplar_dosya.read().splitlines()

# Soru sayısına göre rastgele soruları seç
soru_cevap = random.sample(list(zip(sorular, cevaplar)), len(sorular))

def cevapkontrol(cevap):
    global soru_index
    if soru_index < len(soru_cevap):  # Kullanılabilir soru sayısını kontrol et
        dogru_soru_cevap = soru_cevap[soru_index]

        if cevap.upper() == dogru_soru_cevap[1].upper():  # Doğru cevabı kontrol et (büyük/küçük harf duyarlılığı yok)
            # Doğru cevabın veritabanında olup olmadığını kontrol et
            cursor.execute("SELECT * FROM dogru_cevaplar WHERE soru = ? AND cevap = ?", (dogru_soru_cevap[0], dogru_soru_cevap[1]))
            existing_record = cursor.fetchone()

            if not existing_record:
                # Eğer doğru cevap daha önce eklenmemişse, veritabanına ekleyin
                cursor.execute("INSERT INTO dogru_cevaplar VALUES (?, ?)", (dogru_soru_cevap[0], dogru_soru_cevap[1]))
                baglanti.commit()
            
            dogru_cevaplar.append(dogru_soru_cevap)
        else:
            yanlis_cevaplar.append(soru_cevap[soru_index])

    sonraki_soru()  # Yeni bir soru göster
     

soru_index = -1
dogru_cevaplar = []
yanlis_cevaplar = []

def secenekleri_guncelle():
    dogru_cevap = soru_cevap[soru_index][1].upper()
    secenekler = [dogru_cevap]
    while len(secenekler) < 4:
        rasgele_cevap = random.choice(cevaplar).upper()
        if rasgele_cevap not in secenekler:
            secenekler.append(rasgele_cevap)
    random.shuffle(secenekler)
    return secenekler

def sonraki_soru():
    global soru_index
    soru_index += 1
    if soru_index < len(soru_cevap):  # Kullanılabilir soru sayısını kontrol et
        secilen_soru, dogru_cevap = soru_cevap[soru_index]
        secenekler = secenekleri_guncelle()
        secenekA_button.config(text=f"A. {secenekler[0]}", command=lambda: cevapkontrol(secenekler[0]))
        secenekB_button.config(text=f"B. {secenekler[1]}", command=lambda: cevapkontrol(secenekler[1]))
        secenekC_button.config(text=f"C. {secenekler[2]}", command=lambda: cevapkontrol(secenekler[2]))
        secenekD_button.config(text=f"D. {secenekler[3]}", command=lambda: cevapkontrol(secenekler[3]))
        soru_label.config(text=f"Soru {soru_index + 1}: {secilen_soru}")
        soru_label.config(font=15)
        soru_label.pack(pady=(10, 10))

    else:
        sonuc_goster() 

def sonuc_goster():
    root.withdraw()  # Ana pencereyi gizle
    global sonuc_pencere
    sonuc_pencere = tk.Tk()
    sonuc_pencere.title("Sonuçlar")

    dogru_label = tk.Label(sonuc_pencere, text="Doğru Cevaplar:")
    dogru_label.pack()

    dogru_listbox = tk.Listbox(sonuc_pencere, height=10, width=75)  # Listbox boyutunu ayarla
    dogru_listbox.pack()

    for index, (soru, cevap) in enumerate(dogru_cevaplar):
        dogru_listbox.insert(tk.END, f"{index + 1}. Soru: {soru}, Doğru Cevap: {cevap}")

    yanlis_label = tk.Label(sonuc_pencere, text="Yanlış Cevaplar:")
    yanlis_label.pack()

    yanlis_listbox = tk.Listbox(sonuc_pencere, height=10, width=75)  # Listbox boyutunu ayarla
    yanlis_listbox.pack()

    for index, (soru, cevap) in enumerate(yanlis_cevaplar):
        yanlis_listbox.insert(tk.END, f"{index + 1}. Soru: {soru}, Yanlış Cevap: {cevap}")

    yeni_sorular_button = tk.Button(sonuc_pencere, text="Yeni Sorular", command=yeni_sorular)
    yeni_sorular_button.pack()
    yeni_sorular_button.config(font=12)
   
    sonuc_pencere.mainloop()


    

def dogru_cevaplar_listesi():
    dogru_cevaplar_pencere = tk.Tk()
    dogru_cevaplar_pencere.title("Doğru Cevaplar Listesi")
    
    # Veritabanından doğru cevapları al
    cursor.execute("SELECT * FROM dogru_cevaplar")
    dogru_cevaplar = cursor.fetchall()
    
    if not dogru_cevaplar:
        dogru_label = tk.Label(dogru_cevaplar_pencere, text="Henüz doğru cevap yok.")
        dogru_label.pack()
    else:
        dogru_listbox = tk.Listbox(dogru_cevaplar_pencere, height=25, width=75)  # Listbox boyutunu ayarla
        dogru_listbox.pack()

        for index, (soru, cevap) in enumerate(dogru_cevaplar):
            dogru_listbox.insert(tk.END, f"{index + 1}. Soru: {soru}, Doğru Cevap: {cevap}")

    dogru_cevaplar_pencere.mainloop()

def veritabani_sifirla():
    # Kullanıcıdan onay almak için bir messagebox göster
    onay = messagebox.askyesno("Veritabanı Sıfırlama", "Veritabanını sıfırlamak istediğinizden emin misiniz?")
    if onay:
        cursor.execute("DELETE FROM dogru_cevaplar")
        messagebox.showinfo("Veritabanı Sıfırlandı", "Veritabanı sıfırlandı. Doğru cevaplar listesi boş.")
        
    

def yeni_sorular():
    global soru_index, dogru_cevaplar, yanlis_cevaplar, soru_cevap
    soru_index = -1
    dogru_cevaplar = []
    yanlis_cevaplar = []
    soru_cevap = random.sample(list(zip(sorular, cevaplar)), len(sorular))
    sonraki_soru()
    root.deiconify()
    sonuc_pencere.withdraw()
    


# Eğer metin belgesindeki tüm sorular veritabanında varsa, tüm soruları sormuşuz demektir.
if not sorular:
    messagebox.showinfo("Tüm Sorular Bitti", "Tüm soruları sormuşunuz. Yeni sorular ekleyin veya veritabanını sıfırlayın.")
    veritabani_sifirla()

# GUI oluştur
root = tk.Tk()
root.title("Soru Cevap Oyunu")
root.geometry("400x300")
root.option_add("*Font", "Arial 12")

soru_label = tk.Label(root, text="")
soru_label.pack()

#secenek_label = tk.Label(root, text="Şıklar:")
#secenek_label.pack()

secenekA_button = tk.Button(root, text="", command=lambda: cevapkontrol(secenekA_button.cget("text")[3:]))
secenekA_button.pack()

secenekB_button = tk.Button(root, text="", command=lambda: cevapkontrol(secenekB_button.cget("text")[3:]))
secenekB_button.pack()

secenekC_button = tk.Button(root, text="", command=lambda: cevapkontrol(secenekC_button.cget("text")[3:]))
secenekC_button.pack()

secenekD_button = tk.Button(root, text="", command=lambda: cevapkontrol(secenekD_button.cget("text")[3:]))
secenekD_button.pack()

dogru_cevaplar_button = tk.Button(root, text="Doğru Cevaplar Listesi", command=dogru_cevaplar_listesi)
dogru_cevaplar_button.pack(side=tk.RIGHT)

veritabani_sifirla_button = tk.Button(root, text="Veritabanını Sıfırla", command=veritabani_sifirla)
veritabani_sifirla_button.pack(side=tk.LEFT)

sonuclar_button = tk.Button(root, text="Sonuçlar", command=sonuc_goster)
sonuclar_button.pack(side=tk.BOTTOM)

sonraki_soru()  # İlk 10 soruyu göster
root.mainloop()
