import sqlite3
from datetime import datetime

def baglan():
    # VERİTABANI İSMİ GÜNCELLENDİ
    conn = sqlite3.connect('oto_stok_v1.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS parcalar 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, barkod TEXT, oem_no TEXT, ad TEXT, 
                     arac_detay TEXT, adet INTEGER, alis_fiyat REAL, satis_fiyat REAL, 
                     toplam_satilan INTEGER DEFAULT 0, aciklama TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS satis_gecmisi 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, parca_id INTEGER, musteri_ad TEXT, 
                     adet INTEGER, satis_fiyat REAL, kar REAL, odeme_tipi TEXT, tarih TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS musteriler 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, ad_soyad TEXT UNIQUE, telefon TEXT)''')
    conn.commit()
    return conn

def parca_ekle(barkod, oem_no, ad, arac_detay, adet, alis, satis, aciklama):
    conn = baglan(); cursor = conn.cursor()
    cursor.execute("SELECT id, adet, alis_fiyat FROM parcalar WHERE barkod = ? AND oem_no = ?", (barkod, oem_no))
    sonuc = cursor.fetchone()
    if sonuc:
        p_id, eski_adet, eski_alis = sonuc
        toplam = eski_adet + adet
        yeni_maliyet = ((eski_adet * eski_alis) + (adet * alis)) / toplam if toplam > 0 else alis
        cursor.execute("UPDATE parcalar SET adet=?, alis_fiyat=?, satis_fiyat=?, aciklama=? WHERE id=?", (toplam, yeni_maliyet, satis, aciklama, p_id))
    else:
        cursor.execute("INSERT INTO parcalar (barkod,oem_no,ad,arac_detay,adet,alis_fiyat,satis_fiyat,aciklama) VALUES (?,?,?,?,?,?,?,?)", (barkod, oem_no, ad, arac_detay, adet, alis, satis, aciklama))
    conn.commit(); conn.close()

def satis_yap_db(id_no, miktar, musteri, tel, odeme):
    conn = baglan(); cursor = conn.cursor()
    cursor.execute("SELECT adet, alis_fiyat, satis_fiyat FROM parcalar WHERE id = ?", (id_no,))
    p = cursor.fetchone()
    if p and p[0] >= miktar:
        kar = (p[2] - p[1]) * miktar
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE parcalar SET adet = adet - ?, toplam_satilan = toplam_satilan + ? WHERE id = ?", (miktar, miktar, id_no))
        cursor.execute("INSERT INTO satis_gecmisi (parca_id, musteri_ad, adet, satis_fiyat, kar, odeme_tipi, tarih) VALUES (?,?,?,?,?,?,?)", (id_no, musteri, miktar, p[2], kar, odeme, tarih))
        cursor.execute("INSERT OR IGNORE INTO musteriler (ad_soyad, telefon) VALUES (?,?)", (musteri, tel))
        cursor.execute("UPDATE musteriler SET telefon = ? WHERE ad_soyad = ?", (tel, musteri))
        conn.commit(); conn.close(); return True
    conn.close(); return False

def borc_tahsil_et(satis_id, miktar):
    conn = baglan(); cursor = conn.cursor()
    cursor.execute("SELECT adet, parca_id, satis_fiyat, kar, musteri_ad FROM satis_gecmisi WHERE id = ?", (satis_id,))
    s = cursor.fetchone()
    if s:
        if miktar > s[0]: return "hata_miktar"
        if miktar == s[0]:
            cursor.execute("UPDATE satis_gecmisi SET odeme_tipi = 'ÖDENDİ' WHERE id = ?", (satis_id,))
        else:
            birim_kar = s[3] / s[0]
            cursor.execute("UPDATE satis_gecmisi SET adet = adet - ?, kar = kar - ? WHERE id = ?", (miktar, birim_kar * miktar, satis_id))
            cursor.execute("INSERT INTO satis_gecmisi (parca_id, musteri_ad, adet, satis_fiyat, kar, odeme_tipi, tarih) VALUES (?,?,?,?,?,?,?)",
                           (s[1], s[4], miktar, s[2], birim_kar * miktar, 'ÖDENDİ', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); conn.close(); return "tamam"
    return "hata_id"

def iade_al_db(satis_id, iade_adet):
    conn = baglan(); cursor = conn.cursor()
    cursor.execute("SELECT parca_id, adet, odeme_tipi FROM satis_gecmisi WHERE id = ?", (satis_id,))
    s = cursor.fetchone()
    if s:
        p_id, m_satis_adeti, o_tipi = s
        if iade_adet > m_satis_adeti: 
            conn.close(); return "hata_miktar"
        cursor.execute("UPDATE parcalar SET adet = adet + ?, toplam_satilan = toplam_satilan - ? WHERE id = ?", (iade_adet, iade_adet, p_id))
        if iade_adet == m_satis_adeti:
            cursor.execute("DELETE FROM satis_gecmisi WHERE id = ?", (satis_id,))
            res = "tam_iade"
        else:
            cursor.execute("UPDATE satis_gecmisi SET adet = adet - ?, kar = (kar / (adet)) * (adet - ?) WHERE id = ?", (iade_adet, iade_adet, satis_id))
            res = "parcali_iade"
        conn.commit(); conn.close(); return res
    return "hata_id"

def borc_detay_getir(m_ad):
    conn = baglan(); cursor = conn.cursor()
    cursor.execute('''SELECT s.id, p.ad, s.adet, s.satis_fiyat, s.tarih, mu.telefon 
                      FROM satis_gecmisi s JOIN parcalar p ON s.parca_id = p.id 
                      LEFT JOIN musteriler mu ON s.musteri_ad = mu.ad_soyad
                      WHERE s.musteri_ad = ? AND s.odeme_tipi = 'VERESİYE' ''', (m_ad,))
    v = cursor.fetchall(); conn.close(); return v

def borclu_listesi_getir():
    conn = baglan(); cursor = conn.cursor()
    cursor.execute("SELECT musteri_ad, SUM(adet * satis_fiyat) FROM satis_gecmisi WHERE odeme_tipi = 'VERESİYE' GROUP BY musteri_ad")
    v = cursor.fetchall(); conn.close(); return v

def stok_getir():
    conn = baglan(); cursor = conn.cursor()
    cursor.execute("SELECT id, barkod, oem_no, ad, arac_detay, adet, alis_fiyat, satis_fiyat, toplam_satilan, aciklama FROM parcalar")
    v = cursor.fetchall(); conn.close(); return v

def tum_gecmis_raporlari():
    conn = baglan(); cursor = conn.cursor()
    cursor.execute("SELECT SUBSTR(tarih,1,10) as g, SUM(adet), SUM(satis_fiyat*adet), SUM(kar) FROM satis_gecmisi GROUP BY g ORDER BY g DESC")
    v = cursor.fetchall(); conn.close(); return v

def gunluk_detayli_satislar(tarih):
    conn = baglan(); cursor = conn.cursor()
    cursor.execute('''SELECT s.id, p.ad, s.adet, s.satis_fiyat, s.odeme_tipi, s.tarih, s.musteri_ad, mu.telefon 
                      FROM satis_gecmisi s JOIN parcalar p ON s.parca_id = p.id 
                      LEFT JOIN musteriler mu ON s.musteri_ad = mu.ad_soyad
                      WHERE s.tarih LIKE ? ORDER BY s.tarih DESC''', (f"{tarih}%",))
    v = cursor.fetchall(); conn.close(); return v