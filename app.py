import os
import numpy as np
import pickle

from PIL import Image
from cv2 import resize
from pdf2image import convert_from_path
from flask import Flask, request, redirect, url_for, render_template, flash, send_file
from werkzeug.utils import secure_filename
from easyocr import Reader


app = Flask(__name__, static_folder='static')
path = '../ocr-party/models'


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
    image = convert_from_path(filename)[0]
    image = np.array(image)
    as_pil = Image.fromarray(image)
    # TODO translate 
    # res = reader.readtext(image)
    name = filename.split('.')[0]
    filename = name + '_translated.pdf' 
    as_pil.save('static/' + filename)
    return render_template('translate.html', filename=filename)
        

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join('static', filename))


if __name__ == '__main__':
    # reader = Reader(['pl'], model_storage_directory=path, gpu=True)
    app.run(host='0.0.0.0', debug=True)
    # TODO on leave page delete all static

