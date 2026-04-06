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
        data = request.get_json()

        crop = data.get("crop")
        lat = data.get("lat")
        lon = data.get("lon")

        # PROVERA
        if not crop or lat is None or lon is None:
            return jsonify({"advice": "Nedostaju podaci!"})

        # 🌦️ VREME
        temp = None
        humidity = None

        try:
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
            weather_res = requests.get(weather_url, timeout=5)

            if weather_res.status_code == 200:
                weather_data = weather_res.json()
                temp = weather_data.get("main", {}).get("temp")
                humidity = weather_data.get("main", {}).get("humidity")

        except Exception as e:
            print("Weather error:", str(e))

        # 🤖 FAKE AI LOGIKA

        # ZALIVANJE
        if temp is not None:
            if temp > 30:
                zalivanje = "Povećaj zalivanje (visoka temperatura)"
            elif temp < 15:
                zalivanje = "Smanji zalivanje (niska temperatura)"
            else:
                zalivanje = "Umereno zalivanje"
        else:
            zalivanje = "Nije moguće proceniti (nema podataka o temperaturi)"

        # BOLESTI
        if humidity is not None:
            if humidity > 80:
                bolesti = "Visok rizik od bolesti zbog vlage"
            else:
                bolesti = "Nizak rizik od bolesti"
        else:
            bolesti = "Nije moguće proceniti (nema podataka o vlažnosti)"

        # PRIHRANA
        crop_lower = crop.lower()

        if crop_lower == "paradajz":
            prihrana = "Dodaj kalijum za bolji plod"
        elif crop_lower == "kukuruz":
            prihrana = "Dodaj azot"
        elif crop_lower in ["psenica", "pšenica"]:
            prihrana = "Dodaj NPK đubrivo"
        else:
            prihrana = "Standardna prihrana"

        # FINALNI ODGOVOR
        advice = f"""Zalivanje: {zalivanje}
Bolesti: {bolesti}
Prihrana: {prihrana}"""

        return jsonify({
            "advice": advice
        })

    except Exception as e:
        return jsonify({
            "advice": f"Server error: {str(e)}"
        })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
