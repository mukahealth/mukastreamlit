
GİTHUB 

    Nasıl Çalıştırılır / How to Run

        conda create -n hastalik_env python=3.10
        conda activate hastalik_env
        pip install -r requirements.txt
        streamlit run main.py

📁 notebooks/ klasörü, her hastalık için kullanılan model eğitim süreçlerini ve görselleştirmeleri içerir.

DOCKER : https://hub.docker.com/r/mukahealth/streamlit

    Nasıl Çalıştırılır / How to Run

        Windows / macOS (Docker Desktop)
        docker run -it --privileged -p 8501:8501 mukahealth/streamlit:v* /bin/bash

        Linux
        docker run -it --privileged --network host mukahealth/streamlit:v* /bin/bash


    Uygulama Başlatma / Starting the App

        Container içine girdikten sonra şu komutu çalıştırın:
        After entering the container, run: "start_hastalik"
