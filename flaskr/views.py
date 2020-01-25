import os
import io
import csv

import pandas as pd

from flask import request, redirect, url_for, render_template, flash, send_from_directory
from flask_uploads import UploadSet, DATA, configure_uploads
from werkzeug.utils import secure_filename

from flaskr import app

from libs import PropensityScoreModel


UPLOAD_FOLDER = 'flaskr/data/uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)


@app.route('/')
def index():
    name = "Yamada"
    return render_template('index.html', title='flask test', name=name)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('show_csv', filename=filename))

    return render_template('upload.html', title='Upload new File')


@app.route('/show_csv/<filename>', methods=['GET', 'POST'])
def show_csv(filename):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('show_csv', filename=filename))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    raw_df = pd.read_csv(filepath)

    df = raw_df.copy()
    treatment = 'cm_dummy'
    covariate = [
        'TVwatch_day', 'age', 'sex', 'marry_dummy', 'child_dummy', 'inc', 'pmoney', 'area_kanto',
        'area_tokai', 'area_keihanshin', 'job_dummy1', 'job_dummy2', 'job_dummy3', 'job_dummy4', 'job_dummy5',
        'job_dummy6', 'job_dummy7', 'fam_str_dummy1', 'fam_str_dummy2', 'fam_str_dummy3', 'fam_str_dummy4']
    outcomes = ['gamedummy', 'gamecount', 'gamesecond']

    ps_model = PropensityScoreModel(df, treatment, covariate, outcomes)
    effect = ps_model.estimate_ate().values.tolist()

    return render_template('csv.html', result=zip(outcomes, effect))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
