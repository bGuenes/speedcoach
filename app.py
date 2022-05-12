from flask import Flask, render_template, request, send_from_directory, send_file, redirect, url_for, session
from SpeedCoach import SpeedCoach
import numpy as np
import os
import io

class DataBase(object):
    x = None


data = DataBase()

app = Flask(__name__)

key = os.urandom(16)
app.config.update(SECRET_KEY=key)

@app.route('/', methods = ["GET", "POST"])
def homepage():
    if request.method == "POST":

        varW = request.form["workout"]
        f = request.files['file']
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

    return send_file(return_data, mimetype='application/pdf', attachment_filename=workout+".pdf")


if __name__ == "__main__":
    app.run()