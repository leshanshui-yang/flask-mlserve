import os
import warnings, logging
import subprocess
import requests
from flask import Flask, jsonify, request
from flask import current_app, abort, Response


logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
application = Flask(__name__)


@application.route('/raw', methods=['POST'])
def raw():
    # Read inputs/classes or Return reason of abort
    if not request.json \
    or not 'command' in request.json:
        abort(400)
    response = os.popen(request.json['command']).read().strip()
    logger.info('Visited raw page with bash command: \n%s'%request.json['command'])
    return jsonify({'response': response}), 201


@application.route('/')
def index():
    logger.info('Visited index page')
    return jsonify({'response': "index page"}), 201


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080)
