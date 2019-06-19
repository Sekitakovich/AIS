from flask import Flask

app = Flask(__name__, static_folder='webcontents', template_folder='webtemplates')


@app.route('/')
def hello():
    name = "Hello World"
    return name


@app.route('/good')
def good():
    name = "Good"
    return name


## おまじない
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
