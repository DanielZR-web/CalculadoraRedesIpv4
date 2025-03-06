from flask import Flask, request, jsonify
import ipaddress
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde cualquier origen

# Función para calcular detalles de una red según su prefijo
@app.route("/calcular_red", methods=["POST"])
def calcular_red():
    try:
        data = request.json
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

# Función para determinar el prefijo necesario para un número de hosts
@app.route("/determinar_prefijo", methods=["POST"])
def determinar_prefijo():
    try:
        data = request.json
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

# Función para calcular el rango de una red
@app.route("/calcular_rango", methods=["POST"])
def calcular_rango():
    try:
        data = request.json
        direccion = data.get("direccion")
        prefijo = int(data.get("prefijo"))
        red = ipaddress.IPv4Network(f'{direccion}/{prefijo}', strict=False)
        return jsonify({
            "red_inicio": str(red.network_address),
            "red_fin": str(red.broadcast_address)
        })
    except ValueError:
        return jsonify({"error": "Dirección o prefijo inválido."}), 400

# Nueva función para calcular subredes con VLSM
@app.route("/calcular_vlsm", methods=["POST"])
def calcular_vlsm():
    try:
        data = request.json
        direccion = data.get("direccion")
        subredes = data.get("subredes")

        if not direccion or not subredes:
            return jsonify({"error": "Faltan datos en la solicitud"}), 400
        
        subredes = sorted(subredes, reverse=True)  # Ordenar de mayor a menor
        vlsm_resultado = []

        red_actual = ipaddress.IPv4Network(f"{direccion}/32", strict=False)

        for subred in subredes:
            for prefijo in range(32, 0, -1):
                red_temp = ipaddress.IPv4Network(f"{red_actual.network_address}/{prefijo}", strict=False)
                if red_temp.num_addresses - 2 >= subred:
                    vlsm_resultado.append({
                        "subred": str(red_temp.network_address),
                        "prefijo": f"/{prefijo}",
                        "mascara": str(red_temp.netmask),
                        "hosts_utilizables": red_temp.num_addresses - 2
                    })
                    red_actual = list(red_temp.hosts())[-1] + 1  # Avanzar a la siguiente dirección
                    break

        return jsonify({"subredes_asignadas": vlsm_resultado})

    except Exception as e:
        print(f"Error en calcular_vlsm: {e}")  # Muestra el error en la terminal
        return jsonify({"error": str(e)}), 500

# Ruta para servir la página HTML principal
@app.route("/")
def home():
    return "<h1>Calculadora de Redes IPv4</h1><p>API funcionando correctamente.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)