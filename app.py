from flask import Flask, request, jsonify, render_template
import ipaddress
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde cualquier origen

# Página principal que carga el HTML
@app.route("/")
def home():
    return render_template("index.html")  # Asegúrate de que index.html está en /templates

# 📌 1. Calcular información de la red
@app.route("/calcular_red", methods=["POST"])
def calcular_red():
    data = request.json
    try:
        prefijo = int(data.get("prefijo"))
        red = ipaddress.IPv4Network(f'0.0.0.0/{prefijo}', strict=False)
        total_hosts = red.num_addresses
        hosts_utilizables = total_hosts - 2 if total_hosts > 2 else total_hosts
        return jsonify({
            "total_hosts": total_hosts,
            "hosts_utilizables": hosts_utilizables,
            "mascara": str(red.netmask)
        })
    except ValueError:
        return jsonify({"error": "Prefijo inválido."}), 400

# 📌 2. Determinar prefijo según número de hosts
@app.route("/determinar_prefijo", methods=["POST"])
def determinar_prefijo():
    data = request.json
    try:
        num_hosts = int(data.get("num_hosts"))
        for i in range(32, 0, -1):
            red = ipaddress.IPv4Network(f'0.0.0.0/{i}', strict=False)
            if red.num_addresses - 2 >= num_hosts:
                return jsonify({
                    "prefijo": i,
                    "mascara": str(red.netmask)
                })
        return jsonify({"error": "Número de hosts demasiado grande."}), 400
    except ValueError:
        return jsonify({"error": "Número inválido."}), 400

# 📌 3. Calcular rango de direcciones de una subred
@app.route("/calcular_rango", methods=["POST"])
def calcular_rango():
    data = request.json
    try:
        direccion = data.get("direccion")
        prefijo = int(data.get("prefijo"))
        red = ipaddress.IPv4Network(f'{direccion}/{prefijo}', strict=False)
        return jsonify({
            "red_inicio": str(red.network_address),
            "red_fin": str(red.broadcast_address)
        })
    except ValueError:
        return jsonify({"error": "Dirección o prefijo inválido."}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)