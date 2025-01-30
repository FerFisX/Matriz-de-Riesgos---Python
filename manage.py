from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///risks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo para Activos de Información
class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Modelo para Riesgos
class Risk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    asset = db.relationship('Asset', backref=db.backref('risks', lazy=True))
    threat = db.Column(db.String(200), nullable=False)
    consequence = db.Column(db.String(200), nullable=False)
    probability = db.Column(db.Integer, nullable=False)
    impact = db.Column(db.Integer, nullable=False)
    inherent_risk = db.Column(db.Integer, nullable=False)
    risk_level = db.Column(db.String(50), nullable=False)
    mitigation = db.Column(db.String(200), nullable=True)
    control_type = db.Column(db.String(200), nullable=True)
    control_level = db.Column(db.String(50), nullable=True)
    control_frequency = db.Column(db.String(50), nullable=True)
    residual_probability = db.Column(db.Integer, nullable=False)
    residual_impact = db.Column(db.Integer, nullable=False)
    residual_risk = db.Column(db.Integer, nullable=False)
    residual_level = db.Column(db.String(50), nullable=False)

# Crear la base de datos
with app.app_context():
    db.create_all()

# Función para calcular el nivel de riesgo
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

# Ruta principal
@app.route("/")
def index():
    assets = Asset.query.all()
    risks = Risk.query.all()
    return render_template("index.html", assets=assets, risks=risks)

# Ruta para agregar activos de información
@app.route("/add_asset", methods=["POST"])
def add_asset():
    asset_name = request.form.get("asset")
    if asset_name:
        new_asset = Asset(name=asset_name)
        db.session.add(new_asset)
        db.session.commit()
    return redirect(url_for("index"))

# Ruta para agregar un riesgo
@app.route("/add_risk", methods=["POST"])
def add_risk():
    asset_id = request.form.get("asset")
    threat = request.form.get("threat")
    consequence = request.form.get("consequence")
    probability = int(request.form.get("probability"))
    impact = int(request.form.get("impact"))
    inherent_risk = probability * impact
    risk_level = calculate_risk_level(inherent_risk)
    mitigation = request.form.get("mitigation")
    control_type = ", ".join(request.form.getlist("control_type"))
    control_level = request.form.get("control_level")
    control_frequency = request.form.get("control_frequency")
    residual_probability = int(request.form.get("residual_probability"))
    residual_impact = int(request.form.get("residual_impact"))
    residual_risk = residual_probability * residual_impact
    residual_level = calculate_risk_level(residual_risk)

    new_risk = Risk(
        asset_id=asset_id,
        threat=threat,
        consequence=consequence,
        probability=probability,
        impact=impact,
        inherent_risk=inherent_risk,
        risk_level=risk_level,
        mitigation=mitigation,
        control_type=control_type,
        control_level=control_level,
        control_frequency=control_frequency,
        residual_probability=residual_probability,
        residual_impact=residual_impact,
        residual_risk=residual_risk,
        residual_level=residual_level,
    )
    db.session.add(new_risk)
    db.session.commit()
    return redirect(url_for("index"))

# Ruta para descargar los datos en Excel
@app.route("/download", methods=["GET"])
def download():
    risks = Risk.query.all()

    # Crear un DataFrame con los datos de riesgos
    data = []
    for risk in risks:
        data.append({
            "Activo": risk.asset.name,
            "Amenaza": risk.threat,
            "Consecuencia": risk.consequence,
            "Probabilidad": risk.probability,
            "Impacto": risk.impact,
            "Riesgo Inherente": risk.inherent_risk,
            "Nivel de Riesgo": risk.risk_level,
            "Mitigación": risk.mitigation,
            "Tipo de Control": risk.control_type,
            "Nivel": risk.control_level,
            "Frecuencia": risk.control_frequency,
            "Riesgo Residual": risk.residual_risk,
            "Nivel de Riesgo Residual": risk.residual_level,
        })

    df = pd.DataFrame(data)

    # Guardar el DataFrame en un archivo Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Riesgos')
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="riesgos.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run(debug=True)
