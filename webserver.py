import os
import logging
from multiprocessing import Process
from flask import Flask
from flask import render_template

from common import Constants

app = Flask(__name__, static_folder='webcontents', template_folder='webtemplates')


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")


@app.route('/')
def index():
    name = 'EagleEye'
    return render_template('index.html', name=name)


class Server(Process):

    def __init__(self, *, name: str, osm: str):

        super().__init__()

        self.daemon = True
        self.name = name
        self.osm = osm

        self.logger = logging.getLogger('Log')

    def run(self):

        self.logger.debug(msg='process %d' % os.getpid())
        app.run(debug=False, host='0.0.0.0', port=Constants.wdport)
