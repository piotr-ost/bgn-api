import os

from cv2 import resize
from pdf2image import convert_from_path
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
from easyocr import Reader


app = Flask(__name__, static_folder='uploads')
path = '../ocr-party/models'
reader = Reader(['en'], model_storage_directory=path, gpu=True)


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
            file.save(os.path.join('uploads', filename))
            return redirect(url_for('predict', filename=filename))
    return render_template('home.html')


@app.route('/predict/<filename>')
def predict(filename):
    return render_template('predict.html', filename=filename)

def translate(filename):
    image = convert_from_path(filename)[0]
    image = np.array(image)
    if any(i > 3000 for i in image.shape):
        image = resize(image, None, fx=0.5, fy=0.5)
    res = reader.readtext(image)
    return res

if __name__ == '__main__':
    app.run(port=8011, host='0.0.0.0', debug=True)
