from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    crop = data["crop"]

    result = [
        f"Kultura: {crop}",
        "⚠️ Proveri zalivanje",
        "💧 Moguća suša",
        "🌱 Stanje srednje"
    ]

    return jsonify({
        "ndvi": 0.4,
        "advice": result
    })

app.run()