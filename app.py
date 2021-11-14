from flask import Flask, render_template, request
#import SpeedCoach

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template("home.html")

@app.route("/uploader", methods = ['GET', 'POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        mydata = f.read()
        pl0t = makeprettxpltd(mydata)
        return f.read()

if __name__ == "__main__":
    app.run()
