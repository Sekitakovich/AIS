from flask import Flask
from flask import render_template
from flask import request


app = Flask(__name__, static_folder='../webcontents', template_folder='../webtemplates')

class Main(object):

    def __init__(self):

        app.run(debug=False, host='0.0.0.0', port=8081)


if __name__ == '__main__':

    main = Main()

