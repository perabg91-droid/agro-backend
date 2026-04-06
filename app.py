from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/")
def home():
    return "API radi"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    crop = data.get("crop")
    lat = data.get("lat")
    lon = data.get("lon")

    # Provera
    if not crop or lat is None or lon is None:
        return jsonify({"advice": "Nedostaju podaci!"})

    # 🔥 UZIMANJE VREMENA
    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={os.environ.get('WEATHER_API_KEY')}&units=metric"
        weather_data = requests.get(weather_url).json()

        temp = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
    except:
        temp = "nepoznato"
        humidity = "nepoznato"

    # 🤖 AI PROMPT
    prompt = f"""
Ti si agronom.

Daj konkretan savet za biljku.

Biljka: {crop}
Lokacija: {lat},{lon}
Temperatura: {temp}°C
Vlažnost: {humidity}%

Daj:
- zalivanje
- bolesti
- prihranu

Odgovor neka bude kratak i jasan.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        advice = response.choices[0].message.content

    except Exception as e:
        advice = f"AI error: {str(e)}"

    return jsonify({
        "advice": advice
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
