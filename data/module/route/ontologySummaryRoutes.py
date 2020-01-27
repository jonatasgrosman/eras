import base64
import io
import module.util.routeUtil as RouteUtil
import module.util.ontologyReader as OntologyReader
from flask import request
from module import app


@app.route('/ontology-summary', methods=['POST'])
def ontology_structure():

    if request.json:
        _, b64data = request.json['data'].split(',')
        request.json['bytes'] = base64.b64decode(b64data)

        ontology_string = io.BytesIO(request.json['bytes']).read().decode('UTF-8')

        could_read, result = OntologyReader.read_ontology_as_dict(ontology_string)

        if could_read:
            return RouteUtil.data_to_json_response(result)

    return 'CHECK THE INPUT', 400
