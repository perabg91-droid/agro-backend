from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os

app = Flask(__name__)

# API ključevi
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


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

        # 🌦️ VREME (SIGURNO UZIMANJE)
        temp = "nepoznato"
        humidity = "nepoznato"
        description = "nepoznato"

        try:
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
            weather_res = requests.get(weather_url)

            if weather_res.status_code == 200:
                weather_data = weather_res.json()

                temp = weather_data["main"]["temp"]
                humidity = weather_data["main"]["humidity"]
                description = weather_data["weather"][0]["description"]

        except Exception as e:
            print("Weather error:", str(e))

        # 🤖 AI PROMPT
        prompt = f"""
Ti si iskusan agronom.

Daj konkretan i KRATAK savet farmeru.

Biljka: {crop}
Lokacija: {lat},{lon}
Temperatura: {temp}°C
Vlažnost: {humidity}%
Vreme: {description}

Odgovor format:
- Zalivanje:
- Bolesti:
- Prihrana:
"""

        advice = "Greška sa AI"

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )

            advice = response.choices[0].message.content.strip()

        except Exception as e:
            advice = f"AI error: {str(e)}"

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
