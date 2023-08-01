from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from python_code_converter import PythonCodeConverter

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_code():
    data = request.get_json()
    converter = PythonCodeConverter(data['code'], data['version'])
    converted_code = converter.convert_code()
    return jsonify({'converted_code': converted_code})

if __name__ == '__main__':
    app.run(debug=True)
