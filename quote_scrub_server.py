import os
from flask import Flask, request, redirect, url_for, flash, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask_script import Manager
from quote_scrub import scrub
from time import sleep
from my_logging import print_to_log
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

UPLOAD_FOLDER = 'C:\\uploads'
ALLOWED_EXTENSIONS = set(['xlsx'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


class RequestForm(Form):
    file_reference = FileField('Quote XLSX file:', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/old', methods=['GET', 'POST'])
def upload_file_old():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print_to_log("saved " + os.path.join(app.config['UPLOAD_FOLDER'], filename))
            sleep(3)
            new_filename = scrub(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print_to_log("try to serve " + os.path.basename(new_filename))
            sleep(3)
            if new_filename:
                return redirect(url_for('uploaded_file', filename=os.path.basename(new_filename)))
    return '''
    <!doctype html>
    <title>Quote Scrub</title>
    <h1>Quote XLSX File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    file_reference = None
    form = RequestForm()
    print_to_log("testform upload_file2")
    if form.validate_on_submit():
        print_to_log("form.validate_on_submit")
        file = form.file_reference.data
        form.file_reference.data = ''
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print_to_log("saved " + os.path.join(app.config['UPLOAD_FOLDER'], filename))
            sleep(3)
            try:
                new_filename = scrub(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print_to_log("try to serve " + os.path.basename(new_filename))
                sleep(3)
                if new_filename:
                    return redirect(url_for('uploaded_file', filename=os.path.basename(new_filename)))
                else:
                    return render_template('index.html', form=form, error="Unexpected error, please contact Neil Maldonado")
            except:
                return render_template('index.html', form=form, error="Unexpected error, please contact Neil Maldonado")
        else:
            return render_template('index.html', form=form, error="Please insure quote file is in XLSX format")
    else:
        return render_template('index.html', form=form, error='')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == "__main__":

    manager.run()
