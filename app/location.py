#Kodun karışık olmaması ve modüler olması için bileşen bileşen yazdım. Bu kısım sol sidebardaki mapın konumunu kullanıcıya göre alması için
#enlem boylamını alıyor. Eğer bulamaz ise default olarak ostim teknik üninin kordinatlarını gösteriyor.

from streamlit_javascript import st_javascript

def kullanici_konum(default_enlem=39.968988, default_boylam=32.743764):  # ostim enlem boylam 
    coords = st_javascript("""await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
            (pos) => resolve([pos.coords.latitude, pos.coords.longitude]),  
            (err) => resolve(null)
        );
    });""")
    
    if coords:
        return coords[0], coords[1]   ## cors bir dizi lat 0. elemanı lon 1. elemanı onları test1.py dosyasına return ediyor. 
    else:
        return default_enlem, default_boylam


