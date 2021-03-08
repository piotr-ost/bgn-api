import os
import numpy as np
import pickle
import cv2

from google.cloud import translate_v2
from PIL import Image
from cv2 import resize
from pdf2image import convert_from_path
from flask import Flask, request, redirect, url_for, render_template, flash, send_file
from werkzeug.utils import secure_filename
from easyocr import Reader


app = Flask(__name__, static_folder='static')
path = '../ocr-party/models'


def replace_and_translate(img, points, text, translator):
    [x1, y1], [x2, y1], [x2, y2], [x1, y2] = points
    x1 = int(x1)
    x2 = int(x2)
    y1 = int(y1)
    y2 = int(y2)
    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), -1)
    translated = translator.translate(text)['translatedText']
    print(x1, y1, x2, y2, translated)
    cv2.putText(img, translated, org=(x1, y2), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                color=(0, 0, 0), fontScale=1) # not sure if font size
    return img 


def allowed_file(filename):
    allowed_extensions = {'pdf', 'jpg', 'png'}
    ext_allowed = any([ext for ext in allowed_extensions if ext in filename])
    return '.' in filename and ext_allowed

                                    
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('no file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('no selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('static', filename))
            return redirect(url_for('preview', filename=filename))
    return render_template('home.html')


@app.route('/preview/<filename>')
def preview(filename):
    return render_template('preview.html', filename=filename)


@app.route('/translate/<filename>')
def translate(filename):
    with open('res.pkl', 'rb') as f:
        res = pickle.load(f)
    img = convert_from_path(filename)[0]
    img = np.array(img)
    # res = reader.readtext(image)
    translator = translate_v2.Client()
    for points, text, confidence in res:
        img = replace_and_translate(img, points, text, translator)
    name = filename.split('.')[0]
    filename = name + '_translated_.pdf' 
    as_pil = Image.fromarray(img)
    as_pil.save('static/' + filename)
    return render_template('translate.html', filename=filename)
        

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join('static', filename))


if __name__ == '__main__':
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './key.json'
    # reader = Reader(['pl'], model_storage_directory=path, gpu=True)
    app.run(host='0.0.0.0', debug=True)
    # TODO on leave page delete all static

