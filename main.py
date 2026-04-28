import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import veritabani
import json
import os
import shutil
from datetime import datetime

ctk.set_appearance_mode("dark")

# --- GİRİŞ EKRANI (SPLASH SCREEN) ---
class GirisEkrani(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        genislik, yukseklik = 500, 300
        ekran_g = self.winfo_screenwidth()
        ekran_y = self.winfo_screenheight()
        x = (ekran_g // 2) - (genislik // 2)
        y = (ekran_y // 2) - (yukseklik // 2)
        self.geometry(f"{genislik}x{yukseklik}+{x}+{y}")
        self.frame = ctk.CTkFrame(self, corner_radius=20, border_width=2, border_color="#3498db")
        self.frame.pack(fill="both", expand=True)
        ctk.CTkLabel(self.frame, text="OTO STOK SİSTEMİ", font=("Arial", 28, "bold"), text_color="#3498db").pack(pady=(50, 10))
        ctk.CTkLabel(self.frame, text="Stok Yönetim Sistemi v1.0", font=("Arial", 14)).pack()
        ctk.CTkLabel(self.frame, text="Geliştirici: Tunahan Doğru", font=("Arial", 16, "italic"), text_color="white").pack(pady=30)
        self.progress = ctk.CTkProgressBar(self.frame, width=300)
        self.progress.pack(pady=10)
        self.progress.set(0); self.progress.start()

# --- YARDIMCI SINIFLAR ---
class AracSecici(ctk.CTkToplevel):
    def __init__(self, ana, baslik, veri, var, callback=None):
        super().__init__(ana)
        self.title(baslik); self.geometry("400x500"); self.transient(ana); self.grab_set()
        self.var = var; self.veri = veri; self.callback = callback
        self.e = ctk.CTkEntry(self, placeholder_text=f"{baslik} Ara...", height=40)
        self.e.pack(pady=10, padx=20, fill="x")
        self.e.bind("<KeyRelease>", self.ara)
        self.f = ctk.CTkScrollableFrame(self)
        self.f.pack(expand=True, fill="both", padx=10, pady=10)
        self.yukle(self.veri)

    def yukle(self, l):
        for w in self.f.winfo_children(): w.destroy()
        for i in l: ctk.CTkButton(self.f, text=i, fg_color="transparent", anchor="w",
                                  command=lambda x=i: self.sec(x)).pack(fill="x")

    def ara(self, e):
        self.yukle([i for i in self.veri if self.e.get().lower() in i.lower()])

    def sec(self, d):
        self.var.set(d); self.grab_release(); self.destroy()
        if self.callback: self.callback(d)

class BorcDetay(ctk.CTkToplevel):
    def __init__(self, ana, ad):
        super().__init__(ana)
        self.title(f"Cari: {ad}"); self.geometry("870x600"); self.grab_set()
        f_t = ctk.CTkFrame(self); f_t.pack(fill="both", expand=True, padx=20, pady=10)
        s_b = ttk.Scrollbar(f_t, orient="vertical")
        s_b.pack(side="right", fill="y")
        self.t = ttk.Treeview(f_t, columns=("id", "a", "q", "p", "d", "tel"), show="headings", yscrollcommand=s_b.set)
        for c, h in zip(("id", "a", "q", "p", "d", "tel"), ("ID", "PARÇA", "KALAN", "FİYAT", "TARİH", "TELEFON")):
            self.t.heading(c, text=h); self.t.column(c, width=120, anchor="center")
        self.t.pack(side="left", fill="both", expand=True); s_b.config(command=self.t.yview)
        self.m_ad = ad; self.yukle()
        f_i = ctk.CTkFrame(self); f_i.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f_i, text="Tahsil Adet:").pack(side="left", padx=5)
        self.en_q = ctk.CTkEntry(f_i, width=80); self.en_q.pack(side="left", padx=5); self.en_q.insert(0, "1")
        ctk.CTkButton(f_i, text="TAHSİLAT YAP", fg_color="#27ae60", command=self.yap).pack(side="right", padx=10)

    def yukle(self):
        for i in self.t.get_children(): self.t.delete(i)
        for i in veritabani.borc_detay_getir(self.m_ad): self.t.insert("", "end", values=i)

    def yap(self):
        s = self.t.selection()
        if s:
            try:
                res = veritabani.borc_tahsil_et(self.t.item(s)["values"][0], int(self.en_q.get()))
                if res == "tamam": messagebox.showinfo("Bilgi", "Tahsilat yapıldı."); self.yukle()
                elif res == "hata_miktar": messagebox.showwarning("Hata", "Borçtan fazla miktar!")
            except: messagebox.showerror("Hata", "Geçersiz adet!")

class BorcList(ctk.CTkToplevel):
    def __init__(self, ana):
        super().__init__(ana)
        self.title("Borçlular"); self.geometry("520x480"); self.grab_set()
        f = ctk.CTkFrame(self); f.pack(fill="both", expand=True, padx=20, pady=10)
        s_b = ttk.Scrollbar(f, orient="vertical")
        s_b.pack(side="right", fill="y")
        self.t = ttk.Treeview(f, columns=("a", "b"), show="headings", yscrollcommand=s_b.set)
        self.t.heading("a", text="Müşteri"); self.t.heading("b", text="Toplam Borç")
        self.t.column("a", width=250); self.t.column("b", width=150, anchor="center")
        self.t.pack(side="left", fill="both", expand=True); s_b.config(command=self.t.yview)
        for i in veritabani.borclu_listesi_getir(): self.t.insert("", "end", values=(i[0], f"{i[1]:.2f} ₺"))
        ctk.CTkButton(self, text="DETAYLARI GÖR", command=self.det).pack(pady=10)

    def det(self):
        try:
            s = self.t.selection()
            if s:
                m_ad = self.t.item(s)["values"][0]; self.grab_release()
                BorcDetay(self.master, m_ad); self.destroy()
        except: pass

class Rapor(ctk.CTkToplevel):
    def __init__(self, ana):
        super().__init__(ana)
        self.title("Geçmiş İşlemler"); self.geometry("1150x700"); self.grab_set()
        f_ust = ctk.CTkFrame(self); f_ust.pack(fill="x", padx=20, pady=10)
        s_bar1 = ttk.Scrollbar(f_ust, orient="vertical")
        s_bar1.pack(side="right", fill="y")
        self.t1 = ttk.Treeview(f_ust, columns=("t", "a", "c", "k"), show="headings", height=5, yscrollcommand=s_bar1.set)
        for c, h in zip(("t", "a", "c", "k"), ("TARİH", "ADET", "CİRO", "KÂR")):
            self.t1.heading(c, text=h); self.t1.column(c, width=150, anchor="center")
        self.t1.pack(side="left", fill="x", expand=True); s_bar1.config(command=self.t1.yview)
        self.t1.bind("<<TreeviewSelect>>", self.detay)
        f_alt = ctk.CTkFrame(self); f_alt.pack(fill="both", expand=True, padx=20, pady=10)
        s_bar2 = ttk.Scrollbar(f_alt, orient="vertical")
        s_bar2.pack(side="right", fill="y")
        self.t2 = ttk.Treeview(f_alt, columns=("id", "a", "q", "p", "o", "s", "m", "tel"), show="headings", yscrollcommand=s_bar2.set)
        for c, h in zip(("id", "a", "q", "p", "o", "s", "m", "tel"), ("S_ID", "AD", "ADET", "FİYAT", "TİP", "SAAT", "MÜŞTERİ", "TEL")):
            self.t2.heading(c, text=h); self.t2.column(c, width=100, anchor="center")
        self.t2.pack(side="left", fill="both", expand=True); s_bar2.config(command=self.t2.yview)
        f_i = ctk.CTkFrame(self); f_i.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f_i, text="İade Adet:").pack(side="left", padx=5)
        self.en_i = ctk.CTkEntry(f_i, width=80); self.en_i.pack(side="left", padx=5); self.en_i.insert(0, "1")
        ctk.CTkButton(f_i, text="⚠️ İADE AL", fg_color="#c0392b", command=self.iade).pack(side="right", padx=10)
        for r in veritabani.tum_gecmis_raporlari(): self.t1.insert("", "end", values=(r[0], r[1], f"{r[2]:.2f} ₺", f"{r[3]:.2f} ₺"))

    def detay(self, e):
        try:
            s = self.t1.selection(); t = self.t1.item(s)["values"][0]
            for i in self.t2.get_children(): self.t2.delete(i)
            for d in veritabani.gunluk_detayli_satislar(t): self.t2.insert("", "end", values=d)
        except: pass

    def iade(self):
        s = self.t2.selection()
        if s:
            s_satir = self.t2.item(s)["values"]
            s_id, o_tipi = s_satir[0], s_satir[4]
            try:
                adet = int(self.en_i.get())
                if o_tipi == "VERESİYE":
                    if not messagebox.askyesno("Veresiye İadesi", "Bu ürün VERESİYE satılmıştır. İade borçtan düşülecektir. Onaylıyor musunuz?"): return
                res = veritabani.iade_al_db(s_id, adet)
                if res in ["tam_iade", "parcali_iade"]:
                    messagebox.showinfo("Başarılı", "İade tamamlandı."); self.master.guncelle(); self.destroy()
                elif res == "hata_miktar": messagebox.showwarning("Hata", "Fazla miktar!")
            except: messagebox.showerror("Hata", "Adet girin!")

# --- ANA UYGULAMA ---
class ProfesyonelOtoStok(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.splash = GirisEkrani()
        self.after(3000, self.ana_ekrana_gec)

    def ana_ekrana_gec(self):
        self.splash.destroy()
        self.deiconify()
        self.title("OTO STOK SİSTEMİ")
        self.after(0, lambda: self.state('zoomed'))
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.arac_verisi = {}; self.yukle(); veritabani.baglan()
        self.marka_v = ctk.StringVar(value="Marka Seç..."); self.model_v = ctk.StringVar(value="Model Seç..."); self.alt_v = ctk.StringVar(value="Versiyon Seç...")
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self.sol = ctk.CTkScrollableFrame(self, width=420, label_text="DÜKKAN PANELİ")
        self.sol.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.arayuz_kur(); self.sag_kur()

    def arayuz_kur(self):
        ctk.CTkLabel(self.sol, text="📦 STOK GİRİŞİ", font=("Arial", 12, "bold"), text_color="#3498db").pack(pady=(10, 5))
        self.e_b = self.ekle("Barkod"); self.e_o = self.ekle("OEM"); self.e_a = self.ekle("Parça Adı")
        self.e_al = self.ekle("Alış (₺)"); self.e_sa = self.ekle("Satış (₺)"); self.e_st = self.ekle("Stok Adedi"); self.e_r = self.ekle("Raf Bilgisi")
        ctk.CTkButton(self.sol, textvariable=self.marka_v, command=self.p_m).pack(pady=2, padx=20, fill="x")
        ctk.CTkButton(self.sol, textvariable=self.model_v, command=self.p_mo).pack(pady=2, padx=20, fill="x")
        ctk.CTkButton(self.sol, textvariable=self.alt_v, command=self.p_alt).pack(pady=2, padx=20, fill="x")
        ctk.CTkButton(self.sol, text="📥 STOĞA KAYDET", fg_color="#2ecc71", font=("Arial", 14, "bold"), command=self.kayit).pack(pady=10, padx=20, fill="x")
        ctk.CTkFrame(self.sol, height=2, fg_color="#34495e").pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(self.sol, text="💰 SATIŞ İŞLEMİ", font=("Arial", 12, "bold"), text_color="#e74c3c").pack(pady=(0, 5))
        self.m_ad = self.ekle("Müşteri Ad Soyad"); self.m_tel = self.ekle("Telefon No"); self.m_q = self.ekle("Satış Adet"); self.m_q.insert(0, "1")
        self.o_t = ctk.StringVar(value="NAKİT")
        ctk.CTkSegmentedButton(self.sol, values=["NAKİT", "K. KARTI", "VERESİYE"], variable=self.o_t).pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.sol, text="✅ SATIŞI ONAYLA", fg_color="#e74c3c", height=50, command=self.satis).pack(pady=10, padx=20, fill="x")
        ctk.CTkFrame(self.sol, height=2, fg_color="#34495e").pack(fill="x", padx=20, pady=15)
        ctk.CTkButton(self.sol, text="👥 BORÇ LİSTESİ", fg_color="#f39c12", command=lambda: BorcList(self)).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sol, text="🗓 GEÇMİŞ / İADE", fg_color="#34495e", command=lambda: Rapor(self)).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sol, text="🔄 Yedeği Geri Yükle", fg_color="#2c3e50", height=28, command=self.yedek_geri_yukle).pack(pady=(40, 10), padx=80, fill="x")

    def sag_kur(self):
        f = ctk.CTkFrame(self); f.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.ara = ctk.CTkEntry(f, placeholder_text="🔍 Hızlı Parça Arama...", height=40)
        self.ara.pack(pady=10, padx=20, fill="x"); self.ara.bind("<KeyRelease>", lambda e: self.guncelle(self.ara.get()))
        f_t = ctk.CTkFrame(f); f_t.pack(fill="both", expand=True, padx=10, pady=10)
        s_b = ttk.Scrollbar(f_t, orient="vertical")
        s_b.pack(side="right", fill="y")
        self.t = ttk.Treeview(f_t, columns=("id", "b", "o", "a", "m", "s", "af", "sf", "ts", "ac"), show="headings", yscrollcommand=s_b.set)
        for c, h in zip(("id", "b", "o", "a", "m", "s", "af", "sf", "ts", "ac"), ("ID", "BARKOD", "OEM", "AD", "ARAÇ", "STOK", "ALIŞ", "SATIŞ", "SATILAN", "RAF")):
            self.t.heading(c, text=h); self.t.column(c, width=100, anchor="center")
        self.t.pack(side="left", fill="both", expand=True); s_b.config(command=self.t.yview); self.guncelle()

    def veritabani_yedekle(self):
        try:
            if not os.path.exists("yedekler"): os.makedirs("yedekler")
            k, z = "oto_stok_v1.db", datetime.now().strftime("%Y%m%d_%H%M%S") # YEDEK İSMİ GÜNCELLENDİ
            h = f"yedekler/yedek_{z}.db"
            if os.path.exists(k):
                shutil.copy2(k, h)
                y = sorted([os.path.join("yedekler", f) for f in os.listdir("yedekler")])
                if len(y) > 10: os.remove(y[0])
        except: pass

    def on_closing(self):
        self.veritabani_yedekle(); self.destroy()

    def yedek_geri_yukle(self):
        d = filedialog.askopenfilename(initialdir="yedekler", title="Seç", filetypes=(("DB", "*.db"), ("Hepsi", "*.*")))
        if d:
            if messagebox.askyesno("DİKKAT", "Veriler yedeğin üzerine yazılacak. Emin misiniz?"):
                try:
                    shutil.copy2(d, "oto_stok_v1.db"); self.guncelle() # GERİ YÜKLEME İSMİ GÜNCELLENDİ
                    messagebox.showinfo("Başarılı", "Yüklendi. Lütfen programı kapatıp açın.")
                except Exception as e: messagebox.showerror("Hata", f"Hata: {e}")

    def ekle(self, p):
        e = ctk.CTkEntry(self.sol, placeholder_text=p); e.pack(pady=3, padx=20, fill="x"); return e

    def guncelle(self, f=""):
        for i in self.t.get_children(): self.t.delete(i)
        for p in veritabani.stok_getir():
            if f.lower() in str(p).lower(): self.t.insert("", "end", values=p)

    def kayit(self):
        try:
            al, sa = float(self.e_al.get().replace(",", ".")), float(self.e_sa.get().replace(",", "."))
            d = f"{self.marka_v.get()} {self.model_v.get()} {self.alt_v.get()}"
            veritabani.parca_ekle(self.e_b.get(), self.e_o.get(), self.e_a.get(), d, int(self.e_st.get()), al, sa, self.e_r.get())
            self.guncelle(); messagebox.showinfo("Bilgi", "Kaydedildi."); self.girisleri_temizle()
        except: messagebox.showerror("Hata", "Fiyat/Adet hatası!")

    def satis(self):
        s = self.t.selection()
        if not s: messagebox.showwarning("Uyarı", "Seçim yapın!"); return
        m, t = self.m_ad.get().strip().upper(), self.m_tel.get().strip()
        if not m or not t: messagebox.showwarning("Hata", "Müşteri/Tel eksik!")
        elif veritabani.satis_yap_db(self.t.item(s)["values"][0], int(self.m_q.get()), m, t, self.o_t.get()):
            self.guncelle(); messagebox.showinfo("Başarılı", "Satış Tamam"); self.m_ad.delete(0, 'end'); self.m_tel.delete(0, 'end')
        else: messagebox.showerror("Hata", "Stok yetersiz!")

    def yukle(self):
        try:
            with open('all.json', 'r', encoding='utf-8') as f:
                for i in json.load(f):
                    m, mo, a = i['marka'], i['model'], i['altModel']
                    if m not in self.arac_verisi: self.arac_verisi[m] = {}
                    if mo not in self.arac_verisi[m]: self.arac_verisi[m][mo] = []
                    self.arac_verisi[m][mo].append(a)
        except: pass

    def girisleri_temizle(self):
        for e in [self.e_b, self.e_o, self.e_a, self.e_al, self.e_sa, self.e_st, self.e_r]: e.delete(0, 'end')
        self.marka_v.set("Marka Seç..."); self.model_v.set("Model Seç..."); self.alt_v.set("Versiyon Seç...")

    def p_m(self): AracSecici(self, "Marka", sorted(list(self.arac_verisi.keys())), self.marka_v, self.m_d)
    def m_d(self, _): self.model_v.set("Model Seç..."); self.alt_v.set("Versiyon Seç...")
    def p_mo(self):
        if self.marka_v.get() in self.arac_verisi: AracSecici(self, "Model", sorted(list(self.arac_verisi[self.marka_v.get()].keys())), self.model_v, self.mo_d)
    def mo_d(self, _): self.alt_v.set("Versiyon Seç...")
    def p_alt(self):
        m, mo = self.marka_v.get(), self.model_v.get()
        if m in self.arac_verisi and mo in self.arac_verisi[m]: AracSecici(self, "Versiyon", sorted(self.arac_verisi[m][mo]), self.alt_v)

if __name__ == "__main__":
    ProfesyonelOtoStok().mainloop()