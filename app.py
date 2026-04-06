from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "API radi"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    crop = data.get("crop")
    lat = data.get("lat")
    lon = data.get("lon")

    advice = f"Za {crop} na lokaciji {lat},{lon}: proveri zalivanje i stanje lista."

    return jsonify({
        "advice": advice
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
