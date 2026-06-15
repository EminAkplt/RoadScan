# -*- coding: utf-8 -*-
"""RoadScan akademik makalesini (PDF) üretir — figürler + tablolar dahil."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, HRFlowable)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
FIGS = os.path.join(DOCS, "figs")
os.makedirs(FIGS, exist_ok=True)
OUT = os.path.join(DOCS, "RoadScan_Makale.pdf")

# ---------- Fontlar (Türkçe) ----------
pdfmetrics.registerFont(TTFont("AR", r"C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("ARB", r"C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFont(TTFont("ARI", r"C:/Windows/Fonts/ariali.ttf"))
pdfmetrics.registerFontFamily("AR", normal="AR", bold="ARB", italic="ARI", boldItalic="ARB")

# ---------- Figürler ----------
plt.rcParams["font.size"] = 11
# Fig 1: sınıf bazlı eğitim örnek (kutu) sayısı
cls = ["Boyuna\nÇatlak", "Enine\nÇatlak", "Timsah\nÇatlak", "Çukur"]
train_inst = [22083, 10032, 9025, 18053]
plt.figure(figsize=(6.4, 3.4))
b = plt.bar(cls, train_inst, color=["#3b82f6", "#22c55e", "#f59e0b", "#ef4444"])
plt.ylabel("Eğitim kutu sayısı")
plt.title("Birleşik veri setinde sınıf dağılımı (eğitim)")
for r, v in zip(b, train_inst):
    plt.text(r.get_x() + r.get_width() / 2, v + 300, str(v), ha="center", fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(FIGS, "fig1.png"), dpi=150); plt.close()

# Fig 2: sınıf bazlı mAP@50
cls2 = ["Boyuna", "Enine", "Timsah", "Çukur", "Genel"]
maps = [0.602, 0.603, 0.681, 0.559, 0.611]
plt.figure(figsize=(6.4, 3.4))
b = plt.bar(cls2, maps, color=["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#6b7280"])
plt.ylabel("mAP@50"); plt.ylim(0, 0.8)
plt.title("Sınıf bazlı ve genel mAP@50")
for r, v in zip(b, maps):
    plt.text(r.get_x() + r.get_width() / 2, v + 0.01, f"{v:.3f}", ha="center", fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(FIGS, "fig2.png"), dpi=150); plt.close()

# ---------- Stiller ----------
ss = getSampleStyleSheet()
title = ParagraphStyle("title", parent=ss["Title"], fontName="ARB", fontSize=15, leading=19, alignment=TA_CENTER)
author = ParagraphStyle("author", fontName="ARB", fontSize=11, leading=15, alignment=TA_CENTER)
meta = ParagraphStyle("meta", fontName="AR", fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#333333"))
h1 = ParagraphStyle("h1", fontName="ARB", fontSize=12, leading=16, spaceBefore=12, spaceAfter=5)
h2 = ParagraphStyle("h2", fontName="ARB", fontSize=10.5, leading=14, spaceBefore=8, spaceAfter=3)
body = ParagraphStyle("body", fontName="AR", fontSize=10, leading=14.5, alignment=TA_JUSTIFY, spaceAfter=6)
abst = ParagraphStyle("abst", fontName="AR", fontSize=9.5, leading=13.5, alignment=TA_JUSTIFY)
cap = ParagraphStyle("cap", fontName="ARI", fontSize=8.5, leading=11, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10, textColor=colors.HexColor("#333333"))
eq = ParagraphStyle("eq", fontName="AR", fontSize=10, leading=15, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)
ref = ParagraphStyle("ref", fontName="AR", fontSize=8.5, leading=12, alignment=TA_JUSTIFY, leftIndent=14, firstLineIndent=-14, spaceAfter=3)

S = []
def P(t, st=body): S.append(Paragraph(t, st))
def SP(h=4): S.append(Spacer(1, h))

# ---------- Başlık / yazar ----------
P("Araç İçi Dashcam Görüntülerinden Derin Öğrenme ve Görüntü İşleme ile "
  "Gerçek Zamanlı Yol Bozukluğu Tespiti", title)
SP(8)
P("Mehmet Emin AKPOLAT", author)
P("Fırat Üniversitesi, Teknoloji Fakültesi, Yazılım Mühendisliği Bölümü", meta)
P("215542003@firat.edu.tr", meta)
SP(6); S.append(HRFlowable(width="100%", color=colors.HexColor("#999999"))); SP(8)

# ---------- Öz ----------
P("Öz", h1)
P("Bu çalışma, araç ön kamerasından (dashcam) elde edilen görüntü akışında yoldaki çukur ve çatlak "
  "türü bozuklukları gerçek zamanlı tespit eden, konum ve zaman bilgisiyle eşleştirip merkezi bir "
  "veritabanına raporlayan tam yığın (full-stack) bir sistem önermektedir. Sistem, evrişimsel sinir "
  "ağı tabanlı YOLOv8 nesne tespit modeli ile klasik görüntü işleme yöntemlerini birleştiren hibrit bir "
  "yaklaşım kullanır. Model, üç açık kaynak veri setinin (RDD2022, BharatPotHole, IVCNZ) "
  "birleştirilmesiyle oluşturulan yaklaşık 46.000 görüntülük dört sınıflı (boyuna çatlak, enine çatlak, "
  "timsah sırtı çatlak ve çukur) bir veri kümesi üzerinde transfer öğrenme ile eğitilmiştir. Eğitilen "
  "model doğrulama kümesinde %61 ortalama hassasiyet (mAP@50) elde etmiştir. Tespit edilen "
  "bozukluklar yalnızca derin öğrenme çıktısına bırakılmamış; gökyüzü/yapı gibi yol dışı alanları ve "
  "düz/tek renk yüzeyleri eleyen ROI ve doku (gradyan) tabanlı görüntü işleme süzgeçleriyle "
  "doğrulanarak yanlış pozitiflerin azaltılması hedeflenmiştir. Model ONNX biçimine aktarılarak "
  "tarayıcı üzerinde, internet bağlantısı olmadan, cihaz üstünde çalışacak şekilde dağıtılmıştır. "
  "Sonuçlar, klasik kenar tabanlı yöntemlere kıyasla anlamlı bir doğruluk artışı sağlandığını; saha "
  "verisiyle ince ayar (fine-tuning) yapılarak performansın daha da artırılabileceğini göstermektedir.", abst)
SP(4)
P("<b>Anahtar Kelimeler:</b> Yol bozukluğu tespiti, çukur, derin öğrenme, YOLOv8, nesne tespiti, "
  "görüntü işleme, ONNX, kenar yapay zekâ.", abst)

# ---------- 1. Giriş ----------
P("1. Giriş", h1)
P("Yol yüzeyindeki çukur ve çatlaklar, trafik güvenliğini doğrudan tehdit eden ve araçlarda hasara yol "
  "açan önemli altyapı sorunlarıdır. Bu bozuklukların belediye ve karayolları ekiplerince geleneksel "
  "yöntemlerle tespiti çoğunlukla manuel, yavaş, maliyetli ve dağınık kayıt tutmaya dayalıdır. Son "
  "yıllarda bilgisayarla görme ve derin öğrenme alanındaki gelişmeler, bu sürecin otomatikleştirilmesine "
  "olanak tanımıştır [1], [4].", body)
P("Bu bozuklukların görüntüden tespiti iki temel yaklaşımla ele alınabilir. Birincisi, kenar tespiti, "
  "morfolojik işlemler ve kontur analizi gibi klasik görüntü işleme yöntemleridir. Bu yöntemler "
  "hesaplama açısından hafif olsa da “bozukluk” kavramını öğrenemedikleri için gölge, şerit çizgisi ve "
  "yüzey dokusu gibi her türlü kenarı bozukluk olarak işaretleyerek yüksek oranda yanlış pozitif "
  "üretirler. İkincisi, etiketlenmiş veriden öğrenen evrişimsel sinir ağı (CNN) tabanlı nesne tespit "
  "modelleridir; bunlar bozukluğun görsel örüntüsünü öğrenir ve çok daha az yanlış pozitif üretir [1], [3].", body)
P("Bu çalışmanın katkıları şöyle özetlenebilir: (i) üç açık kaynak veri seti birleştirilerek çukur sınıfı "
  "çok sayıda örnekle desteklenen dört sınıflı bir yol-hasarı veri kümesi oluşturulmuştur; (ii) YOLOv8 "
  "tabanlı bir model transfer öğrenme ile eğitilmiş ve ONNX ile tarayıcıda, çevrimdışı çalışacak şekilde "
  "dağıtılmıştır; (iii) derin öğrenme çıktısı, klasik görüntü işleme tabanlı bir doğrulama katmanıyla "
  "birleştirilerek yanlış pozitifleri azaltan hibrit bir karar mekanizması önerilmiştir; (iv) yalnızca "
  "kritik (yolculuğu etkileyen) bozuklukların raporlanması ve aynı bozukluğun kare-arası takiple tek "
  "kayıt edilmesiyle veritabanı verimliliği sağlanmıştır.", body)

# ---------- 2. Materyal ve Metot ----------
P("2. Materyal ve Metot", h1)

P("2.1. Veri Seti", h2)
P("Çalışmada üç açık kaynak veri seti birleştirilmiştir: RDD2022 (çok uluslu yol hasarı veri seti) [2], "
  "BharatPotHole (çeşitli yol koşullarında dashcam çukur görüntüleri) ve IVCNZ çukur veri seti. Tüm "
  "etiketler ortak bir dört sınıflı düzene (0: boyuna çatlak, 1: enine çatlak, 2: timsah sırtı çatlak, "
  "3: çukur) eşlenmiş; çukur içeren iki ek veri setinin etiketleri çukur sınıfına yönlendirilerek bu sınıf "
  "üç kaynaktan birden beslenmiştir. Birleştirme sonrası elde edilen veri kümesi yaklaşık 46.000 "
  "görüntüden oluşmakta olup eğitim/doğrulama olarak ayrılmıştır (Tablo 1). Sınıf bazlı örnek (kutu) "
  "dağılımı Şekil 1’de verilmiştir.", body)

t1 = Table([["Bölüm", "Görüntü Sayısı"], ["Eğitim (train)", "38.814"], ["Doğrulama (val)", "7.226"],
            ["Toplam", "46.040"]], colWidths=[7*cm, 5*cm])
t1.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,-1), "AR"), ("FONTSIZE", (0,0), (-1,-1), 9.5),
    ("FONTNAME", (0,0), (-1,0), "ARB"), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8eef6")),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#999999")),
    ("ALIGN", (1,0), (1,-1), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
S.append(t1); P("Tablo 1. Birleşik veri setinin eğitim/doğrulama dağılımı.", cap)

S.append(Image(os.path.join(FIGS, "fig1.png"), width=14*cm, height=7.4*cm))
P("Şekil 1. Birleşik veri setinde sınıf bazlı eğitim örneği (sınırlayıcı kutu) sayıları.", cap)

P("2.2. Sistem Mimarisi", h2)
P("Önerilen sistem üç modülden oluşur. (1) Tespit motoru: tarayıcıda çalışan, fotoğraf/video/canlı "
  "kamera kaynaklarını işleyen istemci uygulamasıdır; çıkarım cihaz üstünde, çevrimdışı yapılır. "
  "(2) Veri kayıt servisi: Node.js/Express tabanlı REST API ile gelen tespitleri PostgreSQL "
  "veritabanına kaydeder, kırpılmış görüntüleri dosya olarak saklar. (3) Yönetim paneli: Leaflet "
  "harita üzerinde tespitleri konuma göre gösterir, filtreleme ve özet istatistik sunar. Bu yapı, "
  "modelin sahada (örn. araç içi küçük donanım) çevrimdışı çalışmasına ve bağlantı sağlandığında "
  "merkeze raporlamasına uygundur.", body)

P("2.3. Tespit Modeli (YOLOv8)", h2)
P("Tespit için tek aşamalı (single-stage) bir nesne tespit modeli olan YOLOv8’in küçük (small) "
  "sürümü kullanılmıştır. YOLO ailesi, görüntüyü tek bir ileri besleme ile işleyip sınırlayıcı kutuları "
  "ve sınıf olasılıklarını aynı anda üreterek gerçek zamanlı çalışma sağlar [3]. Evrişim katmanları "
  "görüntüdeki kenar, doku ve şekil gibi özellikleri çıkarırken, ağın tespit başlığı bu özelliklerden "
  "kutu koordinatlarını ve sınıf güvenlerini tahmin eder. Eğitim, COCO veri kümesinde ön-eğitilmiş "
  "ağırlıklardan başlatılarak (transfer öğrenme) gerçekleştirilmiştir [6]. Eğitim hiperparametreleri "
  "Tablo 2’de verilmiştir.", body)

t2 = Table([["Hiperparametre", "Değer"],
            ["Model", "YOLOv8s (small)"],
            ["Başlangıç ağırlığı", "COCO ön-eğitimli (transfer öğrenme)"],
            ["Giriş çözünürlüğü", "640 × 640"],
            ["Paket boyutu (batch)", "16"],
            ["Tur sayısı (epoch)", "80 (erken durdurma: 25)"],
            ["Optimizasyon / öğrenme hızı", "SGD (otomatik) / 0.01"],
            ["Donanım", "NVIDIA RTX 5060 (8 GB)"]], colWidths=[7*cm, 7.5*cm])
t2.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,-1), "AR"), ("FONTSIZE", (0,0), (-1,-1), 9.5),
    ("FONTNAME", (0,0), (-1,0), "ARB"), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8eef6")),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#999999")), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
S.append(t2); P("Tablo 2. Model eğitimi hiperparametreleri.", cap)

P("2.4. Görüntü İşleme Aşamaları", h2)
P("Model, ham haliyle değil, klasik görüntü işleme adımlarıyla çevrelenmiş bir hat (pipeline) içinde "
  "çalışır. <b>Ön işleme:</b> her kare, en-boy oranı korunarak 640×640 boyutuna mektup-kutusu "
  "(letterbox) yöntemiyle ölçeklenir, [0,1] aralığına normalize edilir ve modelin beklediği tensör "
  "biçimine dönüştürülür. <b>Son işleme:</b> modelin ham çıktısı ayrıştırılır, güven eşiğinin altındaki "
  "tespitler elenir ve örtüşen kutular maksimum olmayan baskılama (Non-Maximum Suppression, NMS) "
  "ile birleştirilir; kutular özgün görüntü koordinatlarına geri ölçeklenir.", body)
P("<b>Hibrit doğrulama (klasik görüntü işleme):</b> Bir tespit “kritik” olarak raporlanmadan önce iki "
  "görüntü işleme süzgecinden geçirilir. (i) İlgi alanı (ROI) süzgeci: kutu merkezi görüntünün üst "
  "bölgesindeyse (gökyüzü, bina, ağaç gibi yol dışı alanlar) tespit reddedilir. (ii) Doku/kenar süzgeci: "
  "kutu bölgesi gri tonlamaya çevrilir ve gradyan (Sobel benzeri kenar yoğunluğu) hesaplanır; düz/tek "
  "renk yüzeyler (araç paneli, duvar, boş asfalt) düşük gradyan ürettiğinden reddedilir, çünkü gerçek "
  "bozukluklar belirgin kenar ve dokuya sahiptir. Bu hibrit yapı, derin öğrenmenin öğrenme gücüyle "
  "klasik görüntü işlemenin yorumlanabilir kurallarını birleştirerek yanlış pozitifleri azaltır.", body)
P("<b>Önem (severity) ve raporlama:</b> Her tespitin önem derecesi, sınırlayıcı kutu alanının kareye "
  "oranına ve sınıfına göre Küçük/Orta/Kritik olarak belirlenir. Üç kademe de ekranda görselleştirilir; "
  "ancak veritabanına yalnızca kritik bozukluklar gönderilir. Videoda aynı fiziksel bozukluğun yüzlerce "
  "karede tekrar kaydedilmesini önlemek için kareler arası IoU tabanlı bir takip uygulanır ve her "
  "bozukluk tek kayıt olarak raporlanır.", body)

P("2.5. Performans Metrikleri", h2)
P("Nesne tespitinde başarı, bir tespitin doğru sayılması için tahmin kutusu ile gerçek kutu arasındaki "
  "örtüşme oranının (Intersection over Union, IoU) belirli bir eşiği aşması koşuluna dayanır. Doğru "
  "Pozitif (TP), Yanlış Pozitif (FP) ve Yanlış Negatif (FN) sayıları üzerinden Kesinlik (Precision), "
  "Duyarlılık (Recall) ve ortalama hassasiyet (mAP) hesaplanır. İlgili eşitlikler aşağıda verilmiştir.", body)
P("IoU = Kesişim Alanı / Birleşim Alanı", eq)
P("Kesinlik = TP / (TP + FP)        Duyarlılık = TP / (TP + FN)", eq)
P("AP = Kesinlik–Duyarlılık eğrisi altındaki alan ;  mAP = sınıflar üzerinde AP ortalaması", eq)
P("Bu çalışmada birincil metrik, IoU eşiği 0.5 olan ortalama hassasiyet (mAP@50) ile daha katı bir "
  "ölçüt olan mAP@50–95’tir.", body)

# ---------- 3. Deneysel Bulgular ----------
P("3. Deneysel Bulgular", h1)
P("Model, NVIDIA RTX 5060 (8 GB) ekran kartında 80 tur boyunca eğitilmiştir. Doğrulama kümesi "
  "(7.226 görüntü) üzerindeki sınıf bazlı ve genel sonuçlar Tablo 3’te, mAP@50 değerlerinin "
  "karşılaştırması ise Şekil 2’de sunulmaktadır.", body)

t3 = Table([["Sınıf", "Kesinlik", "Duyarlılık", "mAP@50", "mAP@50–95"],
            ["Boyuna Çatlak", "0.672", "0.549", "0.602", "0.334"],
            ["Enine Çatlak", "0.654", "0.565", "0.603", "0.304"],
            ["Timsah Çatlak", "0.703", "0.638", "0.681", "0.366"],
            ["Çukur", "0.654", "0.527", "0.559", "0.245"],
            ["Genel (ortalama)", "0.671", "0.570", "0.611", "0.312"]],
           colWidths=[4.6*cm, 2.5*cm, 2.5*cm, 2.4*cm, 2.5*cm])
t3.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,-1), "AR"), ("FONTSIZE", (0,0), (-1,-1), 9.5),
    ("FONTNAME", (0,0), (-1,0), "ARB"), ("FONTNAME", (0,-1), (-1,-1), "ARB"),
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8eef6")),
    ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#f3f4f6")),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#999999")),
    ("ALIGN", (1,0), (-1,-1), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
S.append(t3); P("Tablo 3. Doğrulama kümesinde sınıf bazlı ve genel performans.", cap)

S.append(Image(os.path.join(FIGS, "fig2.png"), width=14*cm, height=7.4*cm))
P("Şekil 2. Sınıf bazlı ve genel mAP@50 değerleri.", cap)

P("Sonuçlar incelendiğinde en yüksek başarı timsah sırtı çatlak sınıfında (mAP@50 = 0.681) elde "
  "edilmiştir; bu sınıf geniş ve dokulu bir bozulma örüntüsüne sahip olduğundan modelce daha kolay "
  "ayırt edilmiştir. Boyuna ve enine çatlaklar benzer düzeyde (≈0.60) performans göstermiştir. Çukur "
  "sınıfı, çok sayıda örnekle desteklenmesine rağmen görsel çeşitliliği (suyla dolu, gölgeli, farklı boyut "
  "ve açılarda) nedeniyle nispeten daha düşük (0.559) sonuç vermiştir. Genel mAP@50 değeri 0.611 "
  "olarak ölçülmüştür; bu değer, çok uluslu ve dört sınıflı gerçek dünya yol-hasarı verisi için literatürle "
  "uyumlu, makul bir seviyedir.", body)

# ---------- 4. Tartışma ve Sonuçlar ----------
P("4. Tartışma ve Sonuçlar", h1)
P("Bu çalışmada, dashcam görüntülerinden yol bozukluğu tespiti için derin öğrenme ile klasik görüntü "
  "işlemeyi birleştiren hibrit, çevrimdışı çalışabilen bir sistem geliştirilmiştir. Klasik yalnızca-kenar "
  "tabanlı yöntemlere kıyasla, öğrenen bir modelin kullanılması yanlış pozitifleri belirgin biçimde "
  "azaltmış; ROI ve doku tabanlı görüntü işleme süzgeçleri ise yol dışı ve düz yüzey kaynaklı hatalı "
  "tespitlerin veritabanına gönderilmesini engellemiştir. Modelin ONNX biçiminde dağıtılması, internet "
  "gerektirmeden tarayıcıda ve potansiyel olarak araç içi küçük donanımlarda çalışmasına olanak tanır.", body)
P("Çalışmanın temel sınırı, modelin ağırlıklı olarak yurt dışı (Hindistan/Japonya vb.) yol "
  "görüntüleriyle eğitilmiş olmasıdır; bu nedenle yerel (Türkiye) yol koşullarında, özellikle suyla dolu "
  "veya aşırı bozulmuş çukurlarda yakalama oranı (recall) sınırlı kalmaktadır. Güven eşiği ve görüntü "
  "işleme süzgeçleri bu durumu kısmen iyileştirse de asıl sınırlayıcı etmen eğitim verisinin alan "
  "(domain) uyumudur.", body)
P("Gelecek çalışmalarda; (i) yerel yol görüntüleriyle ince ayar (fine-tuning) yapılarak alan uyumunun "
  "ve çukur yakalama oranının artırılması, (ii) GPS entegrasyonu ve konuma dayalı kümeleme ile "
  "kayıtların daha da sadeleştirilmesi, (iii) çevrimdışı kuyruk (store-and-forward) ile bağlantısız "
  "çalışma, (iv) INT8 nicemleme (quantization) ile gömülü cihazlarda hızlandırma planlanmaktadır. "
  "Sonuç olarak bu çalışma, hibrit (derin öğrenme + görüntü işleme) bir yaklaşımın yol bozukluğu "
  "tespitinde uygulanabilir ve geliştirilebilir bir temel sunduğunu göstermektedir.", body)

# ---------- Kaynaklar ----------
P("Kaynaklar", h1)
refs = [
 '[1] G. Jocher, A. Chaurasia, ve J. Qiu, "Ultralytics YOLOv8," 2023. [Çevrimiçi]. Erişim: https://github.com/ultralytics/ultralytics',
 '[2] D. Arya, H. Maeda, et al., "RDD2022: A multi-national image dataset for automatic road damage detection," Geoscience Data Journal, 2024.',
 '[3] J. Redmon, S. Divvala, R. Girshick, ve A. Farhadi, "You Only Look Once: Unified, Real-Time Object Detection," in Proc. IEEE CVPR, 2016, pp. 779–788.',
 '[4] Y. LeCun, Y. Bengio, ve G. Hinton, "Deep learning," Nature, vol. 521, pp. 436–444, 2015.',
 '[5] T.-Y. Lin et al., "Microsoft COCO: Common Objects in Context," in Proc. ECCV, 2014, pp. 740–755.',
 '[6] A. Krizhevsky, I. Sutskever, ve G. E. Hinton, "ImageNet classification with deep convolutional neural networks," Commun. ACM, vol. 60, no. 6, pp. 84–90, 2017.',
 '[7] Microsoft, "ONNX Runtime," 2024. [Çevrimiçi]. Erişim: https://onnxruntime.ai',
 '[8] R. Padilla, S. L. Netto, ve E. A. B. da Silva, "A survey on performance metrics for object-detection algorithms," in Proc. IWSSIP, 2020.',
]
for r in refs:
    P(r, ref)

# ---------- PDF üret ----------
doc = SimpleDocTemplate(OUT, pagesize=A4, topMargin=2*cm, bottomMargin=1.8*cm,
                        leftMargin=2*cm, rightMargin=2*cm, title="RoadScan", author="Mehmet Emin Akpolat")
doc.build(S)
print("PDF olusturuldu:", OUT)
