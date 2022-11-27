from flask import Flask, render_template, request, send_from_directory, send_file, redirect, url_for, session
from SpeedCoach import SpeedCoach
import numpy as np
import os
import io

class ReverseProxied(object):

    def __init__(self, app, script_name=None, scheme=None, server=None):
        self.app = app
        self.script_name = script_name
        self.scheme = scheme
        self.server = server

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '') or self.script_name
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        scheme = environ.get('HTTP_X_SCHEME', '') or self.scheme
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        server = environ.get('HTTP_X_FORWARDED_SERVER', '') or self.server
        if server:
            environ['HTTP_HOST'] = server
        return self.app(environ, start_response)

class DataBase(object):
    x = None


data = DataBase()

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app, script_name='/speedcoach')

key = os.urandom(16)
app.config.update(SECRET_KEY=key)

@app.route('/', methods = ["GET", "POST"])
def homepage():
    if request.method == "POST":
        
        if request.form["workout"] == "":
            varW = request.files["file"].filename
            varW = varW.rsplit(".")[0]
        else:
            varW = request.form["workout"]

        f = request.files["file"]
        data.x = np.char.split(np.asarray(f.read().decode("utf-8").split("\n")), ",")

        return redirect(url_for("upload", var=varW))

    return render_template("home.html")

@app.route("/<var>")
def upload(var):

    mydata = data.x

    workout = var

    pdfpath, file = SpeedCoach(mydata, workout)

    workingdir = os.path.abspath(os.getcwd())
    pdfpath = workingdir+"/"+"data"+"/"+workout+"/"

    file_path = pdfpath+file

    return_data = io.BytesIO()
    with open(file_path, 'rb') as fo:
        return_data.write(fo.read())
        # (after writing, cursor will be at last byte, so move it to start)
    return_data.seek(0)

    os.remove(file_path)
    os.rmdir(pdfpath)

    return send_file(return_data, mimetype='application/pdf', download_name=workout+".pdf")

@app.route("/backdoor", methods=["POST"])
def compute():
    f = request.files['file']
    data.x = np.char.split(np.asarray(f.read().decode("utf-8").split("\n")), ",")

    mydata = data.x
    workout = request.json["workout"]

    pdfpath, file = SpeedCoach(mydata, workout)

    workingdir = os.path.abspath(os.getcwd())
    pdfpath = workingdir+"/"+"data"+"/"+workout+"/"

    file_path = pdfpath+file

    return_data = io.BytesIO()
    with open(file_path, 'rb') as fo:
        return_data.write(fo.read())
        # (after writing, cursor will be at last byte, so move it to start)
    return_data.seek(0)

    os.remove(file_path)
    os.rmdir(pdfpath)

    return send_file(return_data, mimetype='application/pdf', attachment_filename=workout+".pdf")

if __name__ == "__main__":
    app.run()