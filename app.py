from flask import Flask, request, jsonify, render_template
import ipaddress
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 📌 Página principal que carga el HTML
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

# 📌 4. Cálculo de VLSM
@app.route("/calcular_vlsm", methods=["POST"])
def calcular_vlsm():
    data = request.json
    try:
        red_base = data.get("red_base")
        hosts_list = list(map(int, data.get("hosts", [])))

        if not red_base or not hosts_list:
            return jsonify({"error": "Faltan datos (red base o lista de hosts)."}), 400

        hosts_list.sort(reverse=True)  # Ordenamos de mayor a menor
        subredes = []
        net = ipaddress.IPv4Network(f'{red_base}/32', strict=False)

        for hosts in hosts_list:
            prefijo = 32
            while (2 ** (32 - prefijo)) - 2 < hosts:
                prefijo -= 1
            subred = list(net.subnets(new_prefix=prefijo))[0]
            subredes.append({
                "subred": str(subred.network_address),
                "mascara": str(subred.netmask),
                "rango": f"{subred.network_address} - {subred.broadcast_address}",
                "hosts_utilizables": (subred.num_addresses - 2)
            })
            net = list(net.subnets(new_prefix=prefijo))[1]

        return jsonify(subredes)
    except ValueError:
        return jsonify({"error": "Datos inválidos para VLSM."}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
