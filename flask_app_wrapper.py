from flask import Flask, request, jsonify
from flask_cors import CORS
from python_code_converter import PythonCodeConverter

class FlaskAppWrapper:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/convert', methods=['POST'])
        def convert_code():
            data = request.get_json()
            converter = PythonCodeConverter(data['code'], data['version'])
            converted_code = converter.convert_code()
            return jsonify({'converted_code': converted_code})

    def run(self):
        self.app.run(debug=True)
