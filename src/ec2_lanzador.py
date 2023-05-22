from flask import Flask, request, jsonify

from npl_analyzer_v2 import ejecutar_nlp_texto

app = Flask(__name__)

@app.route('/ejecutar', methods=['POST'])
def ejecutar():
    texto = request.json.get('texto', '')
    datos_serializados = ejecutar_nlp_texto(texto)
    return jsonify(resultado=datos_serializados)

if __name__ == '__main__':
    app.run(debug=True)
