from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Estructuras de datos en memoria
assets = []
threats = []
consequences = []
mitigations = []
risks = []

def calculate_risk_level(risk_value):
    if risk_value <= 5:
        return "Muy Bajo"
    elif risk_value <= 10:
        return "Bajo"
    elif risk_value <= 15:
        return "Medio"
    elif risk_value <= 20:
        return "Alto"
    else:
        return "Crítico"

@app.route("/")
def index():
    return render_template("index.html", 
                           assets=assets, 
                           threats=threats, 
                           consequences=consequences, 
                           mitigations=mitigations, 
                           risks=risks, 
                           probability_options=list(range(1, 6)), 
                           impact_options=list(range(1, 6)), 
                           control_types=["Preventivo", "Detectivo", "Correctivo", "Disuasivo"],
                           control_levels=["Manual", "Automático", "Semi automático"],
                           control_frequencies=["Por evento/req", "Diario", "Semanal", "Mensual", "Semestral", "Anual"])

@app.route("/add_items", methods=["POST"])
def add_items():
    item_type = request.form.get("item_type")
    items = request.form.get("items").split(',')
    target_list = {
        "assets": assets,
        "threats": threats,
        "consequences": consequences,
        "mitigations": mitigations,
    }.get(item_type, [])
    for name in items:
        if name.strip() and name.strip() not in target_list:
            target_list.append(name.strip())
    return redirect(url_for("index"))

@app.route("/add_risk", methods=["POST"])
def add_risk():
    asset = request.form.get("asset")
    threat = request.form.get("threat")
    consequence = request.form.get("consequence")
    probability = int(request.form.get("probability"))
    impact = int(request.form.get("impact"))
    inherent_risk = probability * impact
    risk_level = calculate_risk_level(inherent_risk)
    mitigation = request.form.get("mitigation")
    control_type = request.form.get("control_type")
    control_level = request.form.get("control_level")
    control_frequency = request.form.get("control_frequency")
    residual_probability = int(request.form.get("residual_probability"))
    residual_impact = int(request.form.get("residual_impact"))
    residual_risk = residual_probability * residual_impact
    residual_level = calculate_risk_level(residual_risk)

    new_risk = {
        "asset": asset,
        "threat": threat,
        "consequence": consequence,
        "probability": probability,
        "impact": impact,
        "inherent_risk": inherent_risk,
        "risk_level": risk_level,
        "mitigation": mitigation,
        "control_type": control_type,
        "control_level": control_level,
        "control_frequency": control_frequency,
        "residual_probability": residual_probability,
        "residual_impact": residual_impact,
        "residual_risk": residual_risk,
        "residual_level": residual_level,
    }
    risks.append(new_risk)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
