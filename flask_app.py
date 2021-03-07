import os
import cv2
import logging

from pypoker import Deal
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename

from main import load_models
from runners import run_for_cards


app = Flask(__name__, static_folder='uploads')


def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    return '.' in filename and any([ext for ext in allowed_extensions
                                    if ext in filename])


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
    frame = cv2.imread('uploads/' + filename)
    deal = Deal(log=False)
    cards = []
    out = run_for_cards(frame, deal, detection_model, reader,
                        suit_colors, board=True)
    if out:
        cards += out
    out = run_for_cards(frame, deal, detection_model, reader,
                        suit_colors, board=False)
    if out:
        cards += out
    logging.info(f'{filename}: {cards}')
    return render_template('predict.html', cards=cards, filename=filename)

if __name__ == '__main__':
    logging.basicConfig(filename='ocr-api.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.getLogger().addHandler(logging.StreamHandler())

    detection_model, reader, suit_colors, rdn = load_models()
    app.run(debug=True, use_reloader=False)
