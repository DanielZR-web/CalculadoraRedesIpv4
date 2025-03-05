from flask import Flask, request, jsonify, render_template
import ipaddress
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde cualquier origen

@app.route("/")
def home():
    return render_template("index.html")  # Asegúrate de que el archivo esté en /templates

# Rutas para la API
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
