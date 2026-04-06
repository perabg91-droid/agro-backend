from flask import Flask, request, jsonify, Response
import requests
import os
import base64
import time

app = Flask(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
SENTINEL_CLIENT_ID = os.getenv("SENTINEL_CLIENT_ID")
SENTINEL_CLIENT_SECRET = os.getenv("SENTINEL_CLIENT_SECRET")


# 🔑 SENTINEL TOKEN
def get_sentinel_token():
    url = "https://services.sentinel-hub.com/oauth/token"

    res = requests.post(url, data={
        "grant_type": "client_credentials",
        "client_id": SENTINEL_CLIENT_ID,
        "client_secret": SENTINEL_CLIENT_SECRET
    })

    return res.json().get("access_token")


@app.route("/")
def home():
    return "API radi 🚀"


# 📸 + 🌦️ ANALIZA
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json

        crop = data.get("crop")
        lat = data.get("lat")
        lon = data.get("lon")
        image = data.get("image")

        if not crop or lat is None or lon is None:
            return jsonify({"advice": "Nedostaju podaci!"})

        # 🌦️ VREME
        temp = None
        humidity = None

        if WEATHER_API_KEY:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
                r = requests.get(url, timeout=5)

                if r.status_code == 200:
                    w = r.json()
                    temp = w["main"]["temp"]
                    humidity = w["main"]["humidity"]
            except Exception as e:
                print("WEATHER ERROR:", e)

        # 🤖 AI (BRZI MODE)
        bolest = "Nije analizirano"

        if image and HF_API_KEY:
            try:
                img_bytes = base64.b64decode(image)

                response = requests.post(
                    "https://api-inference.huggingface.co/models/microsoft/resnet-50",
                    headers={
                        "Authorization": f"Bearer {HF_API_KEY}",
                        "Content-Type": "application/octet-stream"
                    },
                    data=img_bytes,
                    timeout=5
                )

                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        bolest = result[0].get("label", "Nepoznato")
                    else:
                        bolest = "AI bez rezultata"
                else:
                    bolest = "AI nedostupan"

            except Exception as e:
                print("AI ERROR:", e)
                bolest = "AI greška"

        # 🌱 LOGIKA
        zalivanje = "Umereno zalivanje"
        if temp is not None:
            if temp > 30:
                zalivanje = "Povećaj zalivanje"
            elif temp < 15:
                zalivanje = "Smanji zalivanje"

        bolesti_rizik = "Nizak rizik"
        if humidity is not None and humidity > 80:
            bolesti_rizik = "Visok rizik od bolesti"

        advice = f"""
Kultura: {crop}

Temperatura: {temp if temp else "?"}°C
Vlažnost: {humidity if humidity else "?"}%

Zalivanje: {zalivanje}
Rizik bolesti: {bolesti_rizik}

AI detekcija: {bolest}
"""

        return jsonify({"advice": advice.strip()})

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"advice": f"Server error: {str(e)}"})


# 🛰️ NDVI (BROJ)
@app.route("/ndvi", methods=["POST"])
def ndvi():
    try:
        data = request.json
        lat = data.get("lat")
        lon = data.get("lon")

        token = get_sentinel_token()

        url = "https://services.sentinel-hub.com/api/v1/process"

        evalscript = """
        //VERSION=3
        function setup() {
          return {
            input: ["B04", "B08"],
            output: { bands: 1 }
          };
        }

        function evaluatePixel(sample) {
          return [(sample.B08 - sample.B04) / (sample.B08 + sample.B04)];
        }
        """

        body = {
            "input": {
                "bounds": {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                },
                "data": [{"type": "sentinel-2-l2a"}]
            },
            "output": {
                "width": 1,
                "height": 1,
                "responses": [{
                    "identifier": "default",
                    "format": {"type": "application/json"}
                }]
            },
            "evalscript": evalscript
        }

        res = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=body
        )

        data = res.json()

        ndvi_value = data["data"][0]["outputs"]["default"]["bands"][0]

        stanje = "Loše"
        if ndvi_value > 0.6:
            stanje = "Zdravo"
        elif ndvi_value > 0.3:
            stanje = "Srednje"

        return jsonify({
            "ndvi": ndvi_value,
            "stanje": stanje
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# 🗺️ NDVI IMAGE (HEATMAP)
@app.route("/ndvi-image", methods=["POST"])
def ndvi_image():
    try:
        data = request.json
        lat = data.get("lat")
        lon = data.get("lon")

        token = get_sentinel_token()

        evalscript = """
        //VERSION=3
        function setup() {
          return {
            input: ["B04", "B08"],
            output: { bands: 3 }
          };
        }

        function evaluatePixel(sample) {
          let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);

          if (ndvi < 0.2) return [1, 0, 0];
          else if (ndvi < 0.5) return [1, 1, 0];
          else return [0, 1, 0];
        }
        """

        body = {
            "input": {
                "bounds": {
                    "bbox": [
                        lon - 0.01,
                        lat - 0.01,
                        lon + 0.01,
                        lat + 0.01
                    ]
                },
                "data": [{"type": "sentinel-2-l2a"}]
            },
            "output": {
                "width": 512,
                "height": 512,
                "responses": [{
                    "identifier": "default",
                    "format": {"type": "image/png"}
                }]
            },
            "evalscript": evalscript
        }

        res = requests.post(
            "https://services.sentinel-hub.com/api/v1/process",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=body
        )

        return Response(res.content, content_type="image/png")

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
