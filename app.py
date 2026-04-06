from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

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

        # PROVERA
        if not crop or lat is None or lon is None:
            return jsonify({"advice": "Nedostaju podaci!"})

        # 🌦️ VREME
        temp = "nepoznato"
        humidity = "nepoznato"

        try:
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
            weather_res = requests.get(weather_url)

            if weather_res.status_code == 200:
                weather_data = weather_res.json()
                temp = weather_data["main"]["temp"]
                humidity = weather_data["main"]["humidity"]

        except Exception as e:
            print("Weather error:", str(e))

        # 🤖 FAKE AI LOGIKA

        # ZALIVANJE
        if temp != "nepoznato":
            if temp > 30:
                zalivanje = "Povećaj zalivanje (visoka temperatura)"
            elif temp < 15:
                zalivanje = "Smanji zalivanje (niska temperatura)"
            else:
                zalivanje = "Umereno zalivanje"
        else:
            zalivanje = "Proveri ručno zalivanje"

        # BOLESTI
        if humidity != "nepoznato" and humidity > 80:
            bolesti = "Visok rizik od bolesti zbog vlage"
        else:
            bolesti = "Nizak rizik od bolesti"

        # PRIHRANA
        crop_lower = crop.lower()

        if crop_lower == "paradajz":
            prihrana = "Dodaj kalijum za bolji plod"
        elif crop_lower == "kukuruz":
            prihrana = "Dodaj azot"
        elif crop_lower == "psenica" or crop_lower == "pšenica":
            prihrana = "Dodaj NPK đubrivo"
        else:
            prihrana = "Standardna prihrana"

        advice = f"""
Zalivanje: {zalivanje}
Bolesti: {bolesti}
Prihrana: {prihrana}
"""

        return jsonify({
            "advice": advice.strip()
        })

    except Exception as e:
        return jsonify({
            "advice": f"Server error: {str(e)}"
        })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
