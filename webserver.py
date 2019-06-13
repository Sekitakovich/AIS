import os
import logging
from threading import Thread
from flask import Flask
from flask import render_template
from flask import request

from common import Constants

app = Flask(__name__, static_folder='webcontents', template_folder='webtemplates')


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route('/voyage')
def voyage():
    sog = int(request.args.get('sog', 0))
    cog = int(request.args.get('cog', 0))
    print('sog:cog = %d:%d' % (sog, cog))
    return 'OK'

@app.route('/')
def index():
    name = 'EagleEye'
    return render_template('index.html', name=name)


class Server(Thread):

    def __init__(self, *, name: str = 'Flask'):

        super().__init__()

        self.daemon = True
        self.name = name

        self.logger = logging.getLogger('Log')

    def run(self):

        self.logger.debug(msg='process %d' % os.getpid())
        app.run(debug=False, host='0.0.0.0', port=Constants.wdport)
