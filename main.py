import streamlit as st
from app.location import kullanici_konum
from app.hastaneler import hastane_listesi_al
from app.popup import show_info_modal  # Pop-up modülünü import ediyoruz
import time
from streamlit_modal import Modal
from PIL import Image
import base64
import joblib
import os

st.set_page_config(page_title="AI Tanı Uygulaması", layout="wide")

# Konumu al
lat, lon = kullanici_konum()

print(f"[KONUM] Alınan konum: lat={lat}, lon={lon}")

# Yakındaki hastaneleri al
df = hastane_listesi_al(lat, lon)

show_info_modal()

#...............................................................


#Harita iframe'i oluştur
# map_iframe = f"""
#     <div style="margin-top: 10px;">
#         <iframe 
#             src="https://www.openstreetmap.org/export/embed.html?bbox={float(lon)-0.001}%2C{float(lat)-0.001}%2C{float(lon)+0.001}%2C{float(lat)+0.001}&amp;layer=mapnik&marker={lat}%2C{lon}"
#             width="100%" height="250" frameborder="0" style="border:1px solid #ccc; border-radius:8px; margin-top:20px;">
#         </iframe>
#     </div>
# """

google_map_iframe = f"""
<iframe
    width="100%"
    height="250"
    frameborder="0"
    style="border:1px solid #ccc; border-radius:8px; margin-top:20px;"
    src="https://www.google.com/maps/embed/v1/view?key=AIzaSyDWJp3Kq_24Tpl68-1YuiyNlnd6r_x-cWg&center={lat},{lon}&zoom=15&maptype=roadmap"
    allowfullscreen>
</iframe>
"""



# Sidebar - Yasal Bilgilendirme ESKİ BİLGİLENDİRME KISIMI

# st.sidebar.markdown("""
#     <div style='display: flex; align-items: center;'>
#         <img src='https://cdn-icons-png.flaticon.com/128/2797/2797387.png' width='50' style='margin-right:10px;'/>
#         <div style="font-size: 22px; margin-left: 12px; margin-top: 3px; font-weight: bold;" > Yasal Bilgilendirme </div>
#     </div>
# """, unsafe_allow_html=True)

# st.sidebar.markdown("""
#     <div style='font-size: 12px; margin: 10px 12px; font-weight: bold;'>
#         Bu uygulama yalnızca yapay zeka destekli tahmini sonuçlar üretir. Gerçek sağlık durumunuzun değerlendirilmesi için mutlaka bir sağlık profesyoneline başvurunuz.
#         Uygulama tarafından verilen bilgiler, tıbbi teşhis, tedavi ya da yönlendirme amacı taşımaz.
#         <span style="color: #b00707;">Geliştirici bu sistemin kullanımından doğabilecek herhangi bir sorumluluğu kabul etmez.</span>
#     </div>
# """, unsafe_allow_html=True)

with open("assets/lastlogo.png", "rb") as image_file:
    testmhrs_encoded = base64.b64encode(image_file.read()).decode()


st.sidebar.markdown(f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{testmhrs_encoded}" width="200">
    </div>
""", unsafe_allow_html=True)


with open("assets/e-nabiz.webp", "rb") as image_file:
    encoded = base64.b64encode(image_file.read()).decode()


with open("assets/haritaicon.svg", "rb") as harita_file:
    haritaencoded = base64.b64encode(harita_file.read()).decode("utf-8")

st.sidebar.markdown(f"""
    <style>
        .button-container {{
            display: flex;
            justify-content: center;
            flex-direction: row;
            gap: 10px;
            margin-top: 10px;
        }}
        .mhrs-button {{
            color: rgb(255, 255, 255);
            height: 46px;
            width: 120px;
            padding:10px;
            font-size:16px;
            background-color:#33b9b2;
            border:none;
            border-radius:5px;
            cursor:pointer;
            transition: background-color 0.3s ease;
        }}
        .mhrs-button:hover {{
            background-color: #2f8784;
        }}
        .enabiz-button {{
            background-color: rgb(13, 58, 169);
            border: none;
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
            color: rgb(255, 255, 255);
            height: 46px;
            width: 120px;
            transition: background-color 0.3s ease;
        }}
        .enabiz-button:hover {{
            background-color: #0056b3;
        }}
        .enabiz-button img {{
            height: 20px;
            vertical-align: middle;
        }}
        .harita-button {{   
            height: 46px;
            width: 120px;
            border-radius: 5px;
            border: none;
            background-color: #c10c14;
            margin-top: 7px;
            margin-right: 10px;
            transition: background-color 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            cursor: pointer;
        }}
        .harita-button:hover {{
            background-color: #85080d;
        }}            
    </style>

<div style="text-align: center;">
        <div class="button-container">
            <a href="https://www.mhrs.gov.tr/vatandas//#/" target="_blank">
                <button class="mhrs-button" style= "font-family: montserrat;">Randevu Al</button>
            </a>
            <a href="https://enabiz.gov.tr/" target="_blank">
                <button class="enabiz-button">
                    <img src="data:image/webp;base64,{encoded}" alt="e-Nabız">
                </button>
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown(google_map_iframe, unsafe_allow_html=True)


# st.sidebar.markdown("### ➤ Size Yakın Hastaneler:")
# if not df.empty:
#     for _, row in df.iterrows():
#         maps_url = f"https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lon']}"
#         st.sidebar.markdown(f"[🚑 {row['name']}]({maps_url})", unsafe_allow_html=True)
# else:
#     st.sidebar.info("Yakınlarda hastane bulunamadı.")

# YOL TARİFİ
#.................................................................................................
st.sidebar.markdown("### ➤ Size Yakın Hastaneler:")

if not df.empty:
    for _, row in df.iterrows():
        # Kendi konumun
        origin_lat = lat
        origin_lon = lon

        # Hedef hastanenin konumu
        dest_lat = row['lat']
        dest_lon = row['lon']

        # Yol tarifi linki
        maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin_lat},{origin_lon}&destination={dest_lat},{dest_lon}&travelmode=driving"

        st.sidebar.markdown(
            f"[🚗 {row['name']} - Yol Tarifi]({maps_url})",
            unsafe_allow_html=True
        )
else:
    st.sidebar.info("Yakınlarda hastane bulunamadı.")
#................................................................................................................



tabs = st.tabs(["**Kalp Yetmezliği Tahmini**", "**Hipertansiyon Tahmini**", "**Diyabet Tahmini**"])

with tabs[0]:

    st.header("❤ Kalp Yetmezliği Riski Tahmini")


    age_category = st.selectbox(
        "**Yaş grubunuz hangi aralıktadır?**",
        ["55 üstü", "45-55 arası", "45 yaş altı"],
        key="age_group"
    )

    if age_category == "55 üstü":
        age = 65
    elif age_category == "45-55 arası":
        age = 50
    elif age_category== "45 yaş altı":
        age = 38

    
    #MUSTAFA4..................................................................................
    blood_pressure_category = st.selectbox(
    "**Dinlenme halindeyken ölçülen kan basıncınız hangi aralıkta?**",
    ["120 mmHg altı","120 mmHg üstü"],
    key="blood_pressure_cat",
    help="**Bu değer istirahat halindeyken ölçülen tansiyon değerinizdir. Ölçüm cihazınızdan veya doktorunuzdan aldığınız değeri giriniz.**")

    if blood_pressure_category == "120 mmHg altı":
        blood_pressure = 105
    else:
        blood_pressure = 160
    #MUSTAFA4..................................................................................
    
    #MUSTAFA5..................................................................................
    cholesterol_category = st.selectbox(
    "**Toplam kolesterol seviyeniz hangi aralıkta?**",
    ["200 mg/dL altı","200 mg/dL üstü"],
    key="cholesterol_cat",
    help="**Toplam kolesterol, kanınızdaki yağ düzeylerini gösterir. Bu değer laboratuvar test sonuçlarınızda yer alır.**")

    if cholesterol_category == "200 mg/dL altı":
        cholesterol = 73
    else:
        cholesterol = 150
    #MUSTAFA5..................................................................................


    fasting_blood_sugar = st.radio("**Açlık kan şekeri değeriniz 120 mg/dL'nin üzerinde mi?**", ["> 120 mg/dl", "<= 120 mg/dl"], key="fbs", help="**Açlık kan şekeri en az 8 saatlik açlıktan sonra ölçülen glikoz seviyesidir. 120’nin üzerindeyse diyabet riski taşır.**")
    
    #MUSTAFA6..................................................................................
    max_heart_rate_category = st.selectbox(
    "**Egzersiz sırasında ulaştığınız maksimum kalp hızı hangi aralıktaydı?**",
    ["120 bpm altı", "120-160 bpm arası", "160 bpm üstü"],
    key="max_hr_cat",
    help="**Bu değer, fiziksel efor sırasında ulaştığınız en yüksek nabızdır. Spor sırasında ölçtüğünüz kalp hızı cihazınız varsa buradan bakabilirsiniz.**")


    if max_heart_rate_category == "120 bpm altı":
        max_heart_rate = 100
    elif max_heart_rate_category == "120-160 bpm arası":
        max_heart_rate = 140
    else:
        max_heart_rate = 170
    #MUSTAFA6..................................................................................

    #MUSTAFA7..................................................................................
    old_peak_category = st.selectbox(
    "**EKG'de egzersiz sonrası ST segmentinde çökme gözlemlendiyse miktarı hangi aralıkta?**",
    ["0.5 mm altı", "0.5-2.0 mm arası", "2.0 mm üstü"],
    key="old_peak_cat",
    help="**Bu değer EKG testinde, egzersiz sonrası kalp elektriksel aktivitesindeki değişimi ifade eder. Doktor raporlarında ST segment depresyonu olarak geçer.**")
    
    if old_peak_category == "0.5 mm altı":
        old_peak = 0.2
    elif old_peak_category == "0.5-2.0 mm arası":
        old_peak = 1.0
    else:
        old_peak = 3.0
    #MUSTAFA7..................................................................................

    gender = st.radio("**Cinsiyetinizi belirtir misiniz?**", ["Erkek", "Kadın"], key="gender")
    ecg = st.selectbox("**EKG testinde doktorunuz size hangi sonucu bildirdi?**", ["Normal", "ST", "LVH"], help="**EKG sonuçları genellikle “normal”, “ST segment anormalliği” veya “sol ventrikül hipertrofisi (LVH)” gibi kategorilerde ifade edilir. Doktorunuzun size söylediğini seçin.**")
    exercise_angina = st.selectbox("**Egzersiz sırasında göğüs ağrısı yaşadınız mı?**", ["Hayır", "Evet"], help="**Fiziksel eforla ortaya çıkan göğüs ağrısı kalp problemleriyle ilişkili olabilir. “Evet” veya “Hayır” şeklinde cevaplayın.**")
    st_slope = st.selectbox("**Egzersiz sonrası EKG'de ST segmenti nasıl bir eğim gösterdi?**", ["Up", "Flat", "Down"], help="**Bu değer doktorunuzun EKG yorumunda Up, Flat veya Down şeklinde belirtilebilir. ST eğimi kalp kası oksijenlenmesini yansıtır.**")

    fbs_val = 1 if fasting_blood_sugar == "> 120 mg/dl" else 0
    gender_val = 1 if gender == "Erkek" else 0


    ecg_vec = [0, 0]  
    if ecg == "Normal":
        ecg_vec = [1, 0]
    elif ecg == "ST":
        ecg_vec = [0, 1]

  
    ex_angina = [1] if exercise_angina == "Evet" else [0]

    slope = [0, 0]  
    if st_slope == "Flat":
        slope = [1, 0]
    elif st_slope == "Up":
        slope = [0, 1]

    input_data = [
        age, blood_pressure, cholesterol, fbs_val, max_heart_rate, old_peak,
        gender_val, *ecg_vec, *ex_angina, *slope
    ]

    model = joblib.load("models/heart.pkl")

    if st.button("**Kalp Yetmezliği Riskini Hesapla**"):
        pred = model.predict([input_data])[0]
        prob = model.predict_proba([input_data])[0][1]
        risk_tresh = prob * 100
        st.subheader(f"📊 Kalp Yetmezliği Riski: {prob * 100:.2f}%")

        if risk_tresh < 26:
            st.success("✅ Risk düşük. Şu an ciddi bir sorun görünmüyor.")
            st.info(
                "Sonuçlara göre kalp yetmezliği açısından düşük bir risk seviyesindesiniz. Bu olumlu bir durum olsa da, tamamen risksiz olduğunuz anlamına gelmez. "
                "Düzenli sağlık kontrolleri yaptırmak ve yaşam tarzınızı sağlıklı şekilde sürdürmek, bu düşük riskin korunmasına yardımcı olur. "
                "Beslenme, hareket ve stres yönetimi gibi konulara dikkat etmek, uzun vadede kalp sağlığınızı destekler. "
                "Belirti olmasa bile, belli aralıklarla uzman görüşü almak erken farkındalık için önemlidir."
            )

        elif risk_tresh < 60:
            st.warning("⚠ Orta düzey risk. Dikkatli olunması ve takip edilmesi gerekir.")
            st.info(
                "Değerleriniz kalp yetmezliği riski açısından orta seviyede görünüyor. Bu aşamada belirti olmasa bile dikkatli olunmalı. "
                "Tansiyon, kolesterol ve benzeri değerlerinizi takip etmeniz, gerektiğinde yaşam tarzınızı gözden geçirmeniz fayda sağlayabilir. "
                "Bu risk düzeyinde bir uzmandan görüş almak, hem mevcut durumunuzu netleştirmek hem de ileride alınabilecek önlemleri belirlemek açısından yararlı olur. "
                "Erken hareket etmek, riskin artmasını engelleyebilir."
            )

        else:
            st.error("❗ Yüksek risk. En kısa sürede bir uzmana başvurmanız önerilir.")
            st.info(
                "Sonuçlar kalp yetmezliği açısından yüksek bir risk taşıdığınızı gösteriyor. Bu, vücudunuzda bazı olumsuzlukların oluşabileceği anlamına gelebilir. "
                "Herhangi bir belirti olmasa bile, bu seviyedeki risk ciddiye alınmalı ve uzman değerlendirmesiyle desteklenmelidir. "
                "Özellikle nefes darlığı, yorgunluk ya da çarpıntı gibi belirtiler varsa zaman kaybetmeden bir sağlık kuruluşuna başvurmanız önemlidir. "
                "Kalp sağlığında erken teşhis ve müdahale, ciddi sonuçların önüne geçebilir."
            )

    #TESTTEN SONRA SİLİNECEK..........................
    st.write(" Gönderilen Model Verileri")
    model_input_labels = [
    "Yaş", 
    "Dinlenme Kan Basıncı", 
    "Toplam Kolesterol", 
    "Açlık Kan Şekeri (>120 mg/dl ise 1 değilse 0)", 
    "Maksimum Kalp Hızı", 
    "ST Segment Depresyonu (Old Peak)",
    "Cinsiyet (Erkek=1, Kadın=0)",
    "EKG Sonucu - Normal", 
    "EKG Sonucu - ST Segment Anormallik", 
    "Egzersiz Anjinası (Evet=1, Hayır=0)",
    "ST Eğimi - Flat", 
    "ST Eğimi - Up"
    ]

    for label, value in zip(model_input_labels, input_data):
        st.write(f"- *{label}:* {value}")
    #TESTTEN SONRA SİLİNECEK..........................

with tabs[1]:

    st.header("🩺 Hipertansiyon Riski Tahmini")

    sex_htn = st.selectbox("**Cinsiyetinizi belirtir misiniz?**", [1, 0], key="htn_sex", format_func=lambda x: "Erkek" if x == 1 else "Kadın")

    #MUSTAFA1..................................................
    age_group_htn = st.selectbox(
    "**Yaş grubunuzu seçiniz**",
    ["40 yaş altı", "40-50 yaş arası", "50 yaş üstü"],
    key="htn_age_group"
    )

    
    if age_group_htn == "40 yaş altı":
        age_htn = 35
    elif age_group_htn == "40-50 yaş arası":
        age_htn = 48
    else:
        age_htn = 62
    #MUSTAFA1..................................................


    smoker_htn = st.selectbox("***Sigara kullanıyor musunuz?**", [1, 0], key="htn_smoker", format_func=lambda x: "Evet" if x == 1 else "Hayır", help="**Sigara kullanımı damarların daralmasına ve tansiyonun yükselmesine neden olabilir. Bu bilgi risk analizinde önemlidir.**")

    if smoker_htn == 1:
        fazla_iciyor_mu = st.radio("**Günlük 10'dan fazla sigara içiyor musunuz?**", ["Evet", "Hayır"], key="htn_sigara_miktar", help="**Aşırı sigara tüketimi kalp-damar sistemini ciddi şekilde etkiler. Günlük sigara miktarınızı belirtin.**")
        daily_cigarettes_htn = 20 if fazla_iciyor_mu == "Evet" else 1
    else:
        daily_cigarettes_htn = 0

    bp_med_htn = st.selectbox("**Tansiyon ilacı kullanıyor musunuz?**", [1, 0], key="htn_bp", format_func=lambda x: "Evet" if x == 1 else "Hayır", help="**Daha önce hipertansiyon tanısı aldıysanız ve ilaç kullanıyorsanız bunu belirtiniz.**")
    diabetes_htn = st.selectbox("**Diyabet hastası mısınız?**", [1, 0], key="htn_diab", format_func=lambda x: "Evet" if x == 1 else "Hayır", help="**Diyabet ve hipertansiyon sıklıkla birlikte görülür. Bu bilgi risk değerlendirmesi için önemlidir.**")

    #MUSTAFA UNUTTUGUM KOLESTROL.............................
    
    cholesterol_htn_category = st.selectbox(
    "**Son yapılan kan testinde toplam kolesterol seviyeniz hangi aralıktaydı? (mg/dL)**",
    ["200 mg/dL altı","200 mg/dL üstü"],
    key="htn_chol_cat",
    help="**Kolesterol yüksekliği kalp damar sağlığını etkiler. Laboratuvar sonuçlarınızdan alınan değeri girin.**")

    if cholesterol_htn_category == "200 mg/dL altı":
        cholesterol_htn = 190.0
    else:
        cholesterol_htn = 260.0
        
    #MUSTAFA UNUTTUGUM KOLESTROL.............................

    #MUSTAFA2.................................
    sys_bp_range = st.selectbox(
    "**Sistolik (büyük) tansiyon değeriniz hangi aralıktadır?**",
    ["95-120 mmHg arası", "120 - 135 mmHg arası", "140 - 160 mmHg arası","160 mmHg ve üzeri"],
    key="htn_sys_range",
    help="**Sistolik tansiyon kalbin kan pompaladığı andaki basıncı gösterir. Tansiyon aletinden veya doktor raporundan alınabilir.**")

    
    if sys_bp_range == "95-120 mmHg arası":
        sys_bp_htn = 100
    elif sys_bp_range == "120 - 135 mmHg arası":
        sys_bp_htn = 130
    elif sys_bp_range == "140 - 160 mmHg arası":
        sys_bp_htn = 145
    else:
        sys_bp_htn = 162
    #MUSTAFA2.................................

    #MUSTAFA3..................................
    dia_bp_range = st.selectbox(
    "**Diyastolik (küçük) tansiyon değeriniz hangi aralıktadır?**",
    ["75 mmHg ve altı", "75 - 89 mmHg arası", "90 mmHg ve üzeri"],
    key="htn_dia_range",
    help="**Diyastolik tansiyon kalbin gevşediği andaki basıncı gösterir. Tansiyon cihazınızdan öğrenebilirsiniz.**")

    
    if dia_bp_range == "75 mmHg ve altı":
        dia_bp_htn = 70
    elif dia_bp_range == "75 - 89 mmHg arası":
        dia_bp_htn = 80
    else:
        dia_bp_htn = 100
    #MUSTAFA3......................................

    # BMI HESAPLAMA KISMI HİPER!!!
    height_htn = st.number_input("**Boyunuz kaç cm?**", min_value=100, max_value=250, value=170, key="htn_height")
    weight_htn = st.number_input("**Kilonuz kaç kg?**", min_value=30, max_value=200, value=70, key="htn_weight")
    # burası kullanıcıya gönderilen bmı kısmı
    bmi_htn = weight_htn / ((height_htn / 100) ** 2) 

    # burası modele gönderilen bmı kısmı
    bmi_model_input = 20.7 if bmi_htn > 25 else 28.7

    heart_rate_question = st.radio("**Dinlenme sırasında kalp hızınız 90’dan küçük müydü?**", ["Evet", "Hayır"], key="htn_hr_flag", help="**Kalp hızı nabız ölçer cihazlarla veya doktor ölçümleriyle belirlenebilir. Genellikle dakikadaki atım sayısıdır (bpm).**")
    heart_rate_htn = 60 if heart_rate_question == "Evet" else 85

    glucose_altinda_mi = st.radio("**Glukoz (şeker) seviyeniz 95 mg/dL’nin altında mıydı?**", ["Evet", "Hayır"], key="htn_glucose_flag", help="**Açlık glukoz değeri, diyabet ve tansiyon ilişkisini analiz etmemize yardımcı olur. Laboratuvar sonucuna göre işaretleyin.**")
    glucose_htn = 62 if glucose_altinda_mi == "Evet" else 88

    #  Model sırasına göre input
    input_data_htn = [[
        sex_htn, age_htn, smoker_htn, daily_cigarettes_htn, bp_med_htn, diabetes_htn,
        cholesterol_htn, sys_bp_htn, dia_bp_htn, bmi_model_input, heart_rate_htn, glucose_htn
    ]]

    #  Modeli yükle
    htn_model_path = joblib.load("models/hipertansiyon.pkl")

    #  Tahmin işlemi
    if st.button("**Hipertansiyon Riskini Hesapla**"):
        pred_htn = htn_model_path.predict(input_data_htn)[0]
        prob_htn = htn_model_path.predict_proba(input_data_htn)[0][1] * 100

        st.subheader(f"📊 Hipertansiyon Riski: {round(prob_htn, 2)}%")
        
        if prob_htn < 26:
            st.success("✅ Risk düşük. Şu an için ciddi bir sorun görünmüyor.")

            st.info("""
            Mevcut verilere göre hipertansiyon riskiniz düşük seviyededir. 
            Bu, şu an için belirgin bir tehdit bulunmadığını göstermektedir. 
            Ancak hipertansiyon zamanla gelişebilen bir durum olduğundan, ilerleyen dönemlerde düzenli takibin önemi büyüktür. 
            Riskin düşük olması, izlem gereksinimini ortadan kaldırmaz. Belirli aralıklarla ölçüm yapılması faydalı olabilir.
            """)

        elif prob_htn < 60:
            st.warning("⚠ Orta düzey risk. Takip edilmesi gereken bir durum olabilir.")

            st.info("""
            Bulgular, hipertansiyon açısından orta seviyede bir risk durumu oluşturduğunu göstermektedir. 
            Bu aşamada henüz tanı gerektiren bir durum olmayabilir ancak zamanla riskin artma ihtimali mevcuttur. 
            Belirli aralıklarla tansiyon değerlerinin ölçülmesi, olası değişimlerin erken fark edilmesine katkı sağlar. 
            Gerekli görüldüğünde bir sağlık uzmanıyla görüşülmesi değerlendirmeye destek olabilir.
            """)

        else:
            st.error("❗ Risk yüksek. Gecikmeden değerlendirme yapılması gerekebilir.")

            st.info("""
            Veriler hipertansiyon açısından yüksek düzeyde risk taşıdığını göstermektedir. 
            Bu durum, ileriye dönük sağlık sorunları açısından önem taşır ve dikkate alınmalıdır. 
            Herhangi bir belirti olmasa da, bu seviyede bir riskin göz ardı edilmemesi gerekir. 
            Daha kapsamlı bir değerlendirme için sağlık kuruluşuna başvurulması uygun olabilir.
            """)

        

        #  BMI YORUM KISIMI
        bmi_status = ""
        if bmi_htn < 18.5:
            bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre zayıfsınız.**"
        elif 18.5 <= bmi_htn <= 24.9:
            bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre normal kilodasınız.**"
        elif 25.0 <= bmi_htn <= 29.9:
            bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre fazla kilolusunuz.**"
        elif 30.0 <= bmi_htn <= 34.9:
            bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre 1. derece obezitesiniz.**"
        elif 35.0 <= bmi_htn <= 39.9:
            bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre 2. derece obezitesiniz.**"
        else:
            bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre 3. derece (morbid) obezitesiniz.**"

        st.info(f"**💡 Hesaplanan BMI:** {bmi_htn:.2f} — {bmi_status}")

    #TESTTEN SONRA SİLİNECEK....................................
    st.write("### Gönderilen Model Verileri (Hipertansiyon)")
    model_input_labels = [
        "Cinsiyet",
        "Yaş",
        "Sigara Kullanımı",
        "Günlük Sigara Sayısı",
        "Tansiyon İlacı Kullanımı",
        "Diyabet",
        "Toplam Kolesterol",
        "Sistolik Tansiyon",
        "Diyastolik Tansiyon",
        "BMI (modellenmiş değer)",
        "Kalp Hızı",
        "Glukoz Değeri"
    ]

    for label, value in zip(model_input_labels, input_data_htn[0]):
        st.write(f"- *{label}:* {value}")
    #TESTTEN SONRA SİLİNECEK.......................................




with tabs[2]:

    st.header("🍬 Diyabet Riski Tahmini")

    height_diab = st.number_input("**Boyunuz kaç cm?**", min_value=100, max_value=250, value=170, key="diab_height")
    weight_diab = st.number_input("**Kilonuz kaç kg?**", min_value=30, max_value=200, value=70, key="diab_weight")

    # BMI hesaplama
    bmi_diab = weight_diab / ((height_diab / 100) ** 2)

    age_diab = st.slider("**Kaç yaşındasınız?**", 1, 120, 40, key="diab_age")
    genhlth_diab = st.selectbox("**Genel sağlık durumunuzu nasıl değerlendirirsiniz?** (1: Çok İyi, 2: İyi, 3: Orta, 4: Kötü, 5: Çok Kötü)", [1, 2, 3, 4, 5], key="diab_genhlth", help="**Kendi sağlık algınız, yaşam tarzınızı ve hastalık riskinizi etkileyebilir. Kendi değerlendirmenizi giriniz.**")
    highbp_diab = st.radio("**Yüksek tansiyon teşhisi aldınız mı?**", ["Evet", "Hayır"], key="diab_highbp", help="**Hipertansiyon ve diyabet sıklıkla birlikte görülen kronik hastalıklardır. Doktor teşhisine göre belirtiniz.**")

    physhlth_input = st.radio("**Son 30 gün içerisinde fiziksel sağlık sorunları yaşadınız mı?**", ["Evet", "Hayır"], key="diab_physhlth", help="**Sürekli veya geçici bedensel sağlık sorunları, diyabetle bağlantılı olabilir. Kendi gözleminizi belirtin.**")
    physhlth_diab = 2 if physhlth_input == "Evet" else -1.6

    menthlth_input = st.radio("**Son 30 gün içerisinde ruhsal sağlık sorunları yaşadınız mı?**", ["Evet", "Hayır"], key="diab_menthlth", help="**Stres, anksiyete veya depresyon gibi durumlar metabolik hastalıklarla ilişkilendirilebilir. Cevabınızı paylaşın.**")
    menthlth_diab = -1.2 if menthlth_input == "Evet" else 1.2

    highchol_diab = st.radio("**Yüksek kolesterol teşhisi aldınız mı?**", ["Evet", "Hayır"], key="diab_highchol", help="**Kolesterol yüksekliği, insülin direnci ve diyabetle bağlantılı olabilir. Doktor teşhisine göre cevaplayın.**")
    fruits_diab = st.radio("**Günlük meyve tüketiyor musunuz?**", ["Evet", "Hayır"], key="diab_fruits")
    smoker_diab = st.radio("**Sigara kullanıyor musunuz?**", ["Evet", "Hayır"], key="diab_smoker")
    sex_diab = st.radio("**Cinsiyetiniz nedir?**", ["Kadın", "Erkek"], key="diab_sex")
    physactivity_diab = st.radio("**Düzenli olarak egzersiz yapıyor musunuz?**", ["Evet", "Hayır"], key="diab_activity")
    veggies_diab = st.radio("**Günlük sebze tüketiyor musunuz?**", ["Evet", "Hayır"], key="diab_veggies")
    diffwalk_diab = st.radio("**Yürümekte zorluk çekiyor musunuz?**", ["Evet", "Hayır"], key="diab_diff", help="**Hareket kısıtlılığı metabolik bozukluklara zemin hazırlayabilir. Günlük hareket kabiliyetinizi belirtin.**")
    heartdisease_diab = st.radio("**Daha önce kalp hastalığı geçirdiniz mi?**", ["Evet", "Hayır"], key="diab_hd")
    stroke_diab = st.radio("**Daha önce felç geçirdiniz mi?**", ["Evet", "Hayır"], key="diab_stroke")

    # Dönüşüm fonksiyonu
    def to_bin(x): return 1 if x in ["Evet", "Erkek"] else 0

    if 0 <= age_diab <= 24:
        age_diab_group = 1
    elif 25 <= age_diab <= 29:
        age_diab_group = 2
    elif 30 <= age_diab <= 34:
        age_diab_group = 3
    elif 35 <= age_diab <= 39:
        age_diab_group = 4
    elif 40 <= age_diab <= 44:
        age_diab_group = 5
    elif 45 <= age_diab <= 49:
        age_diab_group = 6
    elif 50 <= age_diab <= 54:
        age_diab_group = 7
    elif 55 <= age_diab <= 59:
        age_diab_group = 8
    elif 60 <= age_diab <= 64:
        age_diab_group = 9
    elif 65 <= age_diab <= 69:
        age_diab_group = 10
    elif 70 <= age_diab <= 74:
        age_diab_group = 11
    elif 75 <= age_diab <= 79:
        age_diab_group = 12
    else:
        age_diab_group = 13
    
    # Model sırasına göre giriş verisi
    input_data_diab = [[
        bmi_diab,
        age_diab_group,
        genhlth_diab,
        to_bin(highbp_diab),
        physhlth_diab,
        menthlth_diab,
        to_bin(highchol_diab),
        to_bin(fruits_diab),
        to_bin(smoker_diab),
        to_bin(sex_diab),
        to_bin(physactivity_diab),
        to_bin(veggies_diab),
        to_bin(diffwalk_diab),
        to_bin(heartdisease_diab),
        to_bin(stroke_diab)
    ]]

    diabetes_model = joblib.load("models/diyabet.pkl")

    #  Tahmin işlemi
    if st.button("**Diyabet Riskini Hesapla**"):
        try:
            pred_diab = diabetes_model.predict(input_data_diab)[0]
            prob_diab = diabetes_model.predict_proba(input_data_diab)[0][1] * 100

            st.subheader(f"📊 Tahmini Diyabet Riski: {round(prob_diab, 2)}%") 

            if prob_diab < 26:
                st.success("✅ Risk düşük. Şu an için ciddi bir sorun görünmüyor.")

                st.info("""
                Mevcut değerlendirmeye göre diyabet riskiniz düşük seviyededir. 
                Bu, şu anda kan şekeri düzeninizle ilgili belirgin bir sorun bulunmadığına işaret etmektedir. 
                Ancak diyabet zamanla gelişebilen bir durum olduğundan, belirli aralıklarla kontrol yapılması faydalı olabilir. 
                Riskin düşük olması, izlem ihtiyacını tamamen ortadan kaldırmaz.
                """)

            elif prob_diab < 60:
                st.warning("⚠ Orta düzey risk. Takip edilmesi gerekebilir.")

                st.info("""
                Diyabet riski orta seviyededir. Bu durum, henüz tanı konulmasa da ilerleyen dönemlerde riskin artabileceğine işaret etmektedir. 
                Kan şekeri düzeylerinin izlenmesi ve gerekli görülmesi halinde sağlık uzmanı ile değerlendirme yapılması uygun olabilir. 
                Bu seviyede yapılan erken gözlemler, olası gelişmeleri daha net anlamaya yardımcı olabilir.
                """)

            else:
                st.error("❗ Risk yüksek. Daha ayrıntılı bir değerlendirme gerekebilir.")

                st.info("""
                Sonuçlar, diyabet açısından yüksek düzeyde bir risk bulunduğunu göstermektedir. 
                Bu durumda kan şekeri kontrolünün ayrıntılı şekilde incelenmesi önem kazanır. 
                Belirti olmasa bile bu seviyede riskin göz ardı edilmemesi gerekir. 
                Gecikmeden bir sağlık kuruluşunda değerlendirme yapılması uygun olabilir.
                """)



            #  BMI yorumu
            bmi_status = ""
            if bmi_diab < 18.5:
                bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre zayıfsınız.**"
            elif 18.5 <= bmi_diab <= 24.9:
                bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre normal kilodasınız.**"
            elif 25.0 <= bmi_diab <= 29.9:
                bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre fazla kilolusunuz.**"
            elif 30.0 <= bmi_diab <= 34.9:
                bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre 1. derece obezitesiniz.**"
            elif 35.0 <= bmi_diab <= 39.9:
                bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre 2. derece obezitesiniz.**"
            else:
                bmi_status = "**Dünya Sağlık Örgütü tarafından belirlenmiş resmi BMI aralıklarına göre 3. derece (morbid) obezitesiniz.**"

            st.info(f"**💡 Hesaplanan BMI:** {bmi_diab:.2f} — {bmi_status}")

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

    #TESTTEN SONRA SİLİNECEK.......................................
    st.write("###  Gönderilen Model Verileri (Diyabet)")
    model_input_labels_diab = [
        "Vücut Kitle İndeksi (BMI)",
        "Yaş Grubu",
        "Genel Sağlık Durumu",
        "Yüksek Tansiyon",
        "Fiziksel Sağlık Sorunu",
        "Mental Sağlık Sorunu",
        "Yüksek Kolesterol",
        "Günlük Meyve Tüketimi",
        "Sigara Kullanımı",
        "Cinsiyet",
        "Düzenli Egzersiz",
        "Günlük Sebze Tüketimi",
        "Yürürken Zorluk",
        "Geçmiş Kalp Hastalığı",
        "Geçmiş Felç (Stroke)"
    ]

    for label, value in zip(model_input_labels_diab, input_data_diab[0]):
        st.write(f"- *{label}:* {value}")
    #TESTTEN SONRA SİLİNECEK.......................................