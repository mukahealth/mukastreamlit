import streamlit as st
from app.location import kullanici_konum
from app.hastaneler import hastane_listesi_al
from app.popup import show_info_modal 
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


tabs = st.tabs(["**Kalp Yetmezliği Tahmini**", "**Hipertansiyon Tahmini**", "**Diyabet Tahmini**"])

with tabs[0]:

    st.header("❤️ Kalp Yetmezliği Riski Tahmini")

    age_category = st.selectbox("Yaşınızı seçin:", ["55 yaş altı", "55 yaş üstü"])
    def to_bin_age(x): return 1 if x == "55 yaş üstü" else 0


    blood_pressure_category = st.selectbox(
    "Dinlenme halindeyken ölçülen kan basıncınız hangi aralıktadır?",
    ["135 mmHg altı", "135 mmHg üstü"],
    key="blood_pressure_cat",
    help="Bu değer, istirahat halindeyken ölçülen büyük tansiyon değerinizi ifade eder."
    )
    def to_bin_bp(x): return 1 if x == "135 mmHg üstü" else 0

    cholesterol_category = st.selectbox(
    "Toplam kolesterol seviyeniz hangi aralıktadır?",
    ["200 mg/dL altı", "200 mg/dL üstü"],
    key="cholesterol_cat",
    help="Toplam kolesterol değeri laboratuvar testlerinizde yer alır."
    )
    def to_bin_chol(x): return 1 if x == "200 mg/dL üstü" else 0

    fasting_blood_sugar = st.radio(
    "**Açlık kan şekeri değeriniz 120 mg/dL'nin üzerinde mi?**",
    ["Evet", "Hayır"],
    key="fbs",
    help="**Açlık kan şekeri en az 8 saatlik açlıktan sonra ölçülen glikoz seviyesidir. 120’nin üzerindeyse diyabet riski taşır.**") 
    

    max_heart_rate = st.number_input(
    "**Egzersiz sırasında ulaştığınız maksimum kalp hızı (bpm)**",
    min_value=50,
    max_value=250,
    value=140,
    step=1,
    help="**Bu değer, fiziksel efor sırasında ulaştığınız en yüksek nabızdır. Spor sırasında ölçtüğünüz kalp hızı cihazınız varsa buradan bakabilirsiniz.**",
    key="max_hr_input")


    old_peak_category = st.radio(
    "**Egzersiz sonrası ST segment çökmesi (Oldpeak) 2.0 mm'den büyük mü?**",
    ["Evet", "Hayır"],
    key="old_peak_cat",
    help="**Bu değer EKG testinde, egzersiz sonrası kalp elektriksel aktivitesindeki değişimi ifade eder. Doktor raporlarında ST segment depresyonu olarak geçer.**")
    
    
    gender = st.radio("**Cinsiyetinizi belirtir misiniz?**", ["Erkek", "Kadın"], key="gender")
    
    ecg = st.selectbox("**EKG testinde doktorunuz size hangi sonucu bildirdi?**", ["Normal", "ST", "LVH"], help="**EKG sonuçları genellikle “normal”, “ST segment anormalliği” veya “sol ventrikül hipertrofisi (LVH)” gibi kategorilerde ifade edilir. Doktorunuzun size söylediğini seçin.**")
    
    exercise_angina = st.radio(
    "**Egzersiz sırasında göğüs ağrısı yaşadınız mı?**",
    ["Evet", "Hayır"],
    key="exercise_angina",
    help="**Fiziksel eforla ortaya çıkan göğüs ağrısı kalp problemleriyle ilişkili olabilir. “Evet” veya “Hayır” şeklinde cevaplayın.**"
    )    

    st_slope = st.selectbox("**Egzersiz sonrası EKG'de ST segmenti nasıl bir eğim gösterdi?**", ["Up", "Flat", "Down"], help="**Bu değer doktorunuzun EKG yorumunda Up, Flat veya Down şeklinde belirtilebilir. ST eğimi kalp kası oksijenlenmesini yansıtır.**")

    ecg_vec = [1,0, 0]  # LVH
    if ecg == "Normal":
        ecg_vec = [0,1, 0]
    elif ecg == "ST":
        ecg_vec = [0,0, 1]


      # ST Slope
    slope = [1,0,0]  # Down
    if st_slope == "Flat":
        slope = [0,1,0]
    elif st_slope == "Up":
        slope = [0,0,1] 

  
    def to_bin_heart(x): return 1 if x in ["Evet", "Erkek"] else 0

    input_data = [
        to_bin_age(age_category),to_bin_heart(gender), to_bin_bp(blood_pressure_category), to_bin_chol(cholesterol_category), to_bin_heart(fasting_blood_sugar),
        max_heart_rate,to_bin_heart(exercise_angina),to_bin_heart(old_peak_category),*ecg_vec,*slope
    ]

    model = joblib.load("models/heartv2.pkl")

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


with tabs[1]:

    st.header("🩺 Hipertansiyon Riski Tahmini")

    sex_htn = st.radio("**Cinsiyetiniz nedir?**", ["Kadın", "Erkek"], key="hyp_sex")
    
    age_group_htn = st.selectbox(
        "Yaşınızı seçin:",
        ["50 yaş altı", "50 yaş üstü"],
        key="htn_age_group"
    )
    def to_bin_age_htn(x): return 1 if x == "50 yaş üstü" else 0

    smoker_htn = st.radio("**Sigara kullanıyor musunuz?**", ["Evet", "Hayır"], key="htn_smoker")

    diabetes_htn=st.radio("**Diyabet hastası mısınız?**",["Evet","Hayır"],key="htn_diab")
    
    cholesterol_htn_category = st.selectbox(
    "Son yapılan kan testinde toplam kolesterol seviyeniz:",
    ["200 mg/dL altı", "200 mg/dL üstü"],
    key="htn_chol_cat"
    )
    def to_bin_chol_htn(x): return 1 if x == "200 mg/dL üstü" else 0
    
    sys_bp_range = st.selectbox(
        "Sistolik (büyük) tansiyon değeriniz:",
        ["135 mmHg altı", "135 mmHg üstü"],
        key="htn_sys_range"
    )
    def to_bin_sys(x): return 1 if x == "135 mmHg üstü" else 0

    dia_bp_range = st.selectbox(
    "Diyastolik (küçük) tansiyon değeriniz:",
    ["85 mmHg altı", "85 mmHg üstü"],
    key="htn_dia_range"
    )
    def to_bin_dia(x): return 1 if x == "85 mmHg üstü" else 0
    
    # BMI HESAPLAMA KISMI 
    height_htn = st.number_input("**Boyunuz kaç cm?**", min_value=100, max_value=250, value=170, key="htn_height")
    weight_htn = st.number_input("**Kilonuz kaç kg?**", min_value=30, max_value=200, value=70, key="htn_weight")
    
    # burası kullanıcıya gönderilen bmı kısmı
    bmi_htn = weight_htn / ((height_htn / 100) ** 2) 

    if 0 <= bmi_htn < 18.5:
        bmi_htn_group = 0
    elif 18.5 <= bmi_htn < 25:
        bmi_htn_group = 1
    elif 25 <= bmi_htn < 30:
        bmi_htn_group = 2
    elif 30 <= bmi_htn < 35:
        bmi_htn_group = 3
    elif 35 <= bmi_htn < 40: 
        bmi_htn_group = 4
    else:
        bmi_htn_group = 5


    heart_rate_question = st.radio("**Dinlenme sırasında kalp hızınız 80’dan büyük müydü?**", ["Evet", "Hayır"], key="htn_hr_flag")

    glucose_altinda_mi = st.radio("**Glukoz (şeker) seviyeniz 85 mg/dL’nin üstünde miydi?**", ["Evet", "Hayır"], key="htn_glucose_flag")

    def to_bin_hyp(x): return 1 if x in ["Evet", "Erkek"] else 0

    input_data_htn = [[
        to_bin_hyp(sex_htn), to_bin_age_htn(age_group_htn), to_bin_hyp(smoker_htn), to_bin_hyp(diabetes_htn),
        to_bin_chol_htn(cholesterol_htn_category), to_bin_sys(sys_bp_range), to_bin_dia(dia_bp_range), bmi_htn_group, to_bin_hyp(heart_rate_question), to_bin_hyp(glucose_altinda_mi)
    ]]

    #  Modeli yükle
    htn_model_path = joblib.load("models/hipertansiyonv2.pkl")

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



with tabs[2]:

    st.header("🍬 Diyabet Riski Tahmini")

    height_diab = st.number_input("**Boyunuz kaç cm?**", min_value=100, max_value=250, value=170, key="diab_height")
    
    weight_diab = st.number_input("**Kilonuz kaç kg?**", min_value=30, max_value=200, value=70, key="diab_weight")

    # BMI hesaplama
    bmi_diab = weight_diab / ((height_diab / 100) ** 2)

    age_diab = st.slider("**Kaç yaşındasınız?**", 1, 120, 40, key="diab_age")
    
    genhlth_diab = st.selectbox("**Genel sağlık durumunuzu nasıl değerlendirirsiniz?** (1: Çok İyi, 2: İyi, 3: Orta, 4: Kötü, 5: Çok Kötü)", [1, 2, 3, 4, 5], key="diab_genhlth", help="**Kendi sağlık algınız, yaşam tarzınızı ve hastalık riskinizi etkileyebilir. Kendi değerlendirmenizi giriniz.**")
    
    highbp_diab = st.radio("**Yüksek tansiyon teşhisi aldınız mı?**", ["Evet", "Hayır"], key="diab_highbp", help="**Hipertansiyon ve diyabet sıklıkla birlikte görülen kronik hastalıklardır. Doktor teşhisine göre belirtiniz.**")

    highchol_diab = st.radio("**Yüksek kolesterol teşhisi aldınız mı?**", ["Evet", "Hayır"], key="diab_highchol", help="**Kolesterol yüksekliği, insülin direnci ve diyabetle bağlantılı olabilir. Doktor teşhisine göre cevaplayın.**")
    
    highcholcheck_diab = st.radio("**Kolesterol kontrolünüz var mı mı?**", ["Evet", "Hayır"], key="diab_highcholcheck", help="**Kolesterol yüksekliği, insülin direnci ve diyabetle bağlantılı olabilir. Doktor teşhisine göre cevaplayın.**")

    fruits_and_veggies_diab = st.radio("**Günlük meyve ve sebze tüketiyor musunuz?**", ["Evet", "Hayır"], key="diab_fruits")

    smoker_diab = st.radio("**Sigara kullanıyor musunuz?**", ["Evet", "Hayır"], key="diab_smoker")
   
    sex_diab = st.radio("**Cinsiyetiniz nedir?**", ["Kadın", "Erkek"], key="diab_sex")
    
    physactivity_diab = st.radio("**Düzenli olarak egzersiz yapıyor musunuz?**", ["Evet", "Hayır"], key="diab_activity")

    diffwalk_diab = st.radio("**Yürümekte zorluk çekiyor musunuz?**", ["Evet", "Hayır"], key="diab_diff", help="**Hareket kısıtlılığı metabolik bozukluklara zemin hazırlayabilir. Günlük hareket kabiliyetinizi belirtin.**")
    
    heartdisease_diab = st.radio("**Daha önce kalp hastalığı geçirdiniz mi?**", ["Evet", "Hayır"], key="diab_hd")
    
    stroke_diab = st.radio("**Daha önce felç geçirdiniz mi?**", ["Evet", "Hayır"], key="diab_stroke")
    
    alcholCons_diab = st.radio("**Alkol tüketiyor musunuz?**", ["Evet", "Hayır"], key="diab_AlcholCons")

    # Dönüşüm fonksiyonu
    def to_bin(x): return 1 if x in ["Evet", "Erkek"] else 0

    if 0 <= bmi_diab < 18.5:
        bmi_diab_group = 0
    elif 18.5 <= bmi_diab < 25:
        bmi_diab_group = 1
    elif 25 <= bmi_diab < 30:
        bmi_diab_group = 2
    elif 30 <= bmi_diab < 35:
        bmi_diab_group = 3
    elif 35 <= bmi_diab < 40: 
        bmi_diab_group = 4
    else:
        bmi_diab_group = 5


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
    
    input_data_diab = [[
        age_diab_group,
        to_bin(sex_diab),
        to_bin(highchol_diab),
        to_bin(highcholcheck_diab),
        bmi_diab_group,
        to_bin(smoker_diab),
        to_bin(heartdisease_diab),
        to_bin(physactivity_diab),
        to_bin(alcholCons_diab),
        genhlth_diab,
        to_bin(diffwalk_diab),
        to_bin(stroke_diab),
        to_bin(highbp_diab),
        to_bin(fruits_and_veggies_diab)
    ]]

    diabetes_model = joblib.load("models/diyabetv2.pkl")

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
