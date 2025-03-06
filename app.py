from flask import Flask, request, jsonify, render_template 
import ipaddress 
from flask import Flask, request, jsonify, render_template
import ipaddress
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route("/calcular_vlsm", methods=["POST"])
def calcular_vlsm():
    data = request.json
    try:
        red_base = data.get("red_base")
        subredes = sorted([int(h) for h in data.get("subredes")], reverse=True)
        
        resultados = []
        ip_actual = ipaddress.IPv4Network(f'{red_base}/32', strict=False).network_address
        
        for num_hosts in subredes:
            for i in range(32, 0, -1):
                red = ipaddress.IPv4Network(f'{ip_actual}/{i}', strict=False)
                if red.num_addresses - 2 >= num_hosts:
                    resultados.append({
                        "subred": str(red.network_address),
                        "prefijo": i,
                        "mascara": str(red.netmask),
                        "rango": f"{red.network_address} - {red.broadcast_address}"
                    })
                    ip_actual = red.broadcast_address + 1
                    break
        
        return jsonify(resultados)
    except ValueError:
        return jsonify({"error": "Datos inválidos."}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
