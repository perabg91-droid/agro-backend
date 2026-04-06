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

    # Ako nema podataka
    if not crop or lat is None or lon is None:
        return jsonify({"advice": "Nedostaju podaci!"})

    crop_lower = crop.lower()

    # PAMETNIJI SAVETI
    if crop_lower == "paradajz":
        advice = f"""
Za paradajz na lokaciji {lat},{lon}:

- Proveri vlagu zemljišta (paradajz voli umereno zalivanje)
- Obrati pažnju na plamenjaču (žute mrlje na listu)
- Dodaj prihranu (kalijum za plod)
"""

    elif crop_lower == "kukuruz":
        advice = f"""
Za kukuruz na lokaciji {lat},{lon}:

- Proveri vlagu zemljišta (bitno u fazi rasta)
- Dodaj azotnu prihranu
- Obrati pažnju na korov
"""

    elif crop_lower == "pšenica" or crop_lower == "psenica":
        advice = f"""
Za pšenicu na lokaciji {lat},{lon}:

- Proveri stanje lista (moguće bolesti)
- Prati vlagu zemljišta
- Obrati pažnju na korov
"""

    else:
        advice = f"""
Za biljku {crop} na lokaciji {lat},{lon}:

- Proveri vlagu zemljišta
- Obrati pažnju na štetočine
- Prilagodi zalivanje vremenskim uslovima
"""

    return jsonify({
        "advice": advice.strip()
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
