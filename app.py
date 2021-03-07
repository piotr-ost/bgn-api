from flask import Flask, request, jsonify
from easyocr import Reader


path = '../ocr-party/models'
reader = Reader(['en'], model_storage_directory=path, gpu=True)

app = Flask(__name__)

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    reader.request = request
    return jsonify([[12, 123, 12, 31], ['asdf']])


if __name__ == '__main__':
    app.run(port=8011, host='0.0.0.0', debug=True)

