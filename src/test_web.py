from flask import Flask, request
from npl_analyzer_v2 import ejecutar_nlp_texto
from flask_cors import CORS
import asyncio
import json
import os

app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

@app.route('/analyze', methods=['POST'])
def analyze():

    data = request.get_json()
    texto = data.get('texto')
    print(texto)
    incluir_img = data.get('incluir_img', False)

    os.environ['PRINT_MATRIX'] = 'False'
    os.environ['LOCAL'] = 'False'
    os.environ['PAL_DEBUG'] = 'False'
    os.environ['ZOOM_ACTIVE'] = 'True'
    os.environ['PRINT_IMG'] = 'False'
    os.environ['PRINT_GRAPH'] = 'False'
    os.environ['PICTOGRAM_ACTIVE'] = str(incluir_img)

    print(incluir_img)
    def run_ec2():
        lista_palabras, lista_relaciones, Palabra, Relacion = asyncio.run(ejecutar_nlp_texto(texto, local=True))

    run_ec2()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)


# En mi proximo viaje voy a visitar París en donde podré visitar el Palacio de Versalles, Disney y la Torre Eiffel
# El lunes voy a cocinar un pastel de chocolate, yo necesito huevos, harina, cacao, azúcar y mantequilla.

# IMG:
# Nosotros nos vamos de vacaciones a la playa con el perro
# En verano hace mucho calor en Madrid