from flask import Flask, request, jsonify
import requests
import os
import base64

app = Flask(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

@app.route("/")
def home():
    return "API radi"


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json

        crop = data.get("crop")
        lat = data.get("lat")
        lon = data.get("lon")
        image = data.get("image")  # base64 slika

        if not crop or lat is None or lon is None:
            return jsonify({"advice": "Nedostaju podaci!"})

        # 🌦️ VREME
        temp = "nepoznato"
        humidity = "nepoznato"

        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
            r = requests.get(url)

            if r.status_code == 200:
                w = r.json()
                temp = w["main"]["temp"]
                humidity = w["main"]["humidity"]
        except:
            pass

        # 🤖 AI ZA SLIKU (Hugging Face)
        bolest = "Nije analizirano"

        if image and HF_API_KEY:
            try:
                img_bytes = base64.b64decode(image)

                response = requests.post(
                    "https://api-inference.huggingface.co/models/google/vit-base-patch16-224",
                    headers={"Authorization": f"Bearer {HF_API_KEY}"},
                    data=img_bytes
                )

                if response.status_code == 200:
                    result = response.json()
                    bolest = result[0]["label"]
            except Exception as e:
                bolest = "Greška u AI analizi"

        # 🌱 LOGIKA
        if temp != "nepoznato":
            if temp > 30:
                zalivanje = "Povećaj zalivanje"
            elif temp < 15:
                zalivanje = "Smanji zalivanje"
            else:
                zalivanje = "Umereno zalivanje"
        else:
            zalivanje = "Proveri ručno"

        if humidity != "nepoznato" and humidity > 80:
            bolesti_rizik = "Visok rizik od bolesti"
        else:
            bolesti_rizik = "Nizak rizik"

        advice = f"""
Zalivanje: {zalivanje}
Rizik bolesti: {bolesti_rizik}
AI detekcija: {bolest}
"""

        return jsonify({"advice": advice.strip()})

    except Exception as e:
        return jsonify({"advice": f"Server error: {str(e)}"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
