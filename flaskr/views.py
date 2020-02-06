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
    html_file = 'upload.html'
    filename = request.args.get('filename')
    treatment = request.form.get('treatment')
    covariate = request.form.getlist('covariate')
    outcomes = request.form.getlist('outcomes')

    if treatment is not None and covariate != [] and outcomes != []:
        # Processing for causal inference after select variavles.
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = pd.read_csv(filepath)

        # treatment = 'cm_dummy'
        # covariate = [
        #     'TVwatch_day', 'age', 'sex', 'marry_dummy', 'child_dummy', 'inc', 'pmoney', 'area_kanto',
        #     'area_tokai', 'area_keihanshin', 'job_dummy1', 'job_dummy2', 'job_dummy3', 'job_dummy4', 'job_dummy5',
        #     'job_dummy6', 'job_dummy7', 'fam_str_dummy1', 'fam_str_dummy2', 'fam_str_dummy3', 'fam_str_dummy4']
        # outcomes = ['gamedummy', 'gamecount', 'gamesecond']

        ps_model = PropensityScoreModel(df, treatment, covariate, outcomes)
        effects = ps_model.estimate_ate().values.tolist()

        return render_template(
            html_file,
            title='Upload new File',
            cols=df.columns.tolist(),
            result=zip(outcomes, effects),
            chart_result=zip(outcomes, effects))

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

        # Processing to uploaded csv file.
        if not filename or file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file', filename=filename))

    if filename:
        # Processing for selecting variables.
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = pd.read_csv(filepath)
        return render_template(
            html_file,
            title='Upload New File',
            cols=df.columns.tolist())

    return render_template(html_file, title='Upload New File')
