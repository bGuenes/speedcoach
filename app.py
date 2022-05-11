from flask import Flask, render_template, request, send_from_directory, send_file
from SpeedCoach import SpeedCoach
import csv
import numpy as np
import os
import io



app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template("home.html")

@app.route("/uploader", methods = ['GET', 'POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        mydata = np.char.split(np.asarray(f.read().decode("utf-8").split("\n")), ",")

        workout = request.form["workout"]

        pdfpath, file = SpeedCoach(mydata, workout)

        workingdir = os.path.abspath(os.getcwd())
        pdfpath = workingdir+"/"+"data"+"/"+workout+"/"
        print(pdfpath)

        #return send_from_directory(pdfpath, file), os.remove(pdfpath+file)

        file_path = pdfpath+file

        return_data = io.BytesIO()
        with open(file_path, 'rb') as fo:
            return_data.write(fo.read())
            # (after writing, cursor will be at last byte, so move it to start)
        return_data.seek(0)

        os.remove(file_path)
        os.rmdir(pdfpath)

        return send_file(return_data, mimetype='application/pdf', attachment_filename='download_filename.pdf')


if __name__ == "__main__":
    app.run()