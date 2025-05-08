# modal_bilgilendirme.py

import streamlit as st
from streamlit_modal import Modal

def show_info_modal():
    if "modal_open" not in st.session_state:
        st.session_state.modal_open = True

    

    modal = Modal(
        key="uyari_modal",
        title="⚠️Bilgilendirme ve Yasal Uyarı"
        
    )

    if st.session_state.modal_open:
        with modal.container():
            st.markdown("""
                <div style='text-align: justify; font-size: 15px; line-height: 1.6;'>
                Bu uygulama, kullanıcıların kendi beyanlarına dayalı olarak girdikleri semptom bilgilerini kullanarak, yapay zeka algoritmaları aracılığıyla <strong>ön değerlendirme ve yönlendirici nitelikte öneriler</strong> sunmayı amaçlamaktadır. Ancak burada sunulan hiçbir bilgi, <strong>hekim muayenesi yerine geçmez, tıbbi teşhis veya tedavi amacı taşımaz.</strong> Hayati risk taşıyan, ani gelişen veya acil müdahale gerektiren sağlık problemleri için lütfen gecikmeden <span style="color: red;"> en yakın sağlık kuruluşuna başvurunuz. </span> Yapay zeka destekli bu sistem, yalnızca bir destek aracıdır ve tıbbi uzman görüşünün yerini almaz.

                Sistemin sunduğu bilgiler, bilimsel veri ve algoritmalara dayalı olarak oluşturulmakla birlikte, kişisel sağlık geçmişi, tıbbi tetkikler ve fiziksel muayene gibi unsurlar dikkate alınmadığı için kapsamlı bir değerlendirme sağlamaz. Kullanıcıların sunduğu veriler, sistemin doğruluğunu artırmak ve sürekli geliştirilmesini sağlamak amacıyla <strong>anonim olarak kaydedilebilir ve işlenebilir.</strong>

                Bu uygulamada hiçbir şekilde ad, soyad, kimlik numarası, iletişim bilgisi gibi kişisel olarak tanımlayıcı veri talep edilmemekte ve kaydedilmemektedir. Sistem yalnızca semptomlara ilişkin bilgileri işler ve bu veriler, kişinin kimliğinin doğrudan tespitine imkân vermez. Dolayısıyla toplanan bilgiler, <strong>anonim veri</strong> statüsündedir.


                Kullanıcılar, bu uygulamayı kullanmakla birlikte, burada belirtilen veri işleme ilkelerini ve tıbbi sorumluluk sınırlarını <strong>kabul etmiş sayılır.</strong> Kullanım sırasında doğabilecek herhangi bir doğrudan ya da dolaylı sonuçtan geliştiriciler sorumlu tutulamaz. Bu bildirim, kullanıcıyı korumak ve sistemi şeffaf biçimde tanıtmak amacıyla hazırlanmıştır. Her zaman önceliğiniz, şüpheli durumlarda yetkili bir hekime başvurmak olmalıdır.
                </div>
                """, unsafe_allow_html=True)



            if st.button("Anladım ve Devam Et"):
                st.session_state.modal_open = False
                st.rerun()
