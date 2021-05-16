from flask import Flask

app = Flask(__name__)

@app.route("/berkay")
def test():
    return "<b>test</b>"
@app.route('/')
def hello():
    return 'Fuck you Ufuk ;P'

if __name__ == "__main__":
    app.run()