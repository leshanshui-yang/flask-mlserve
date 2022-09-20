import os
import warnings, logging
import subprocess
import requests
from flask import Flask, jsonify, request
from flask import current_app, abort, Response
import mlflow


logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
application = Flask(__name__)


# Best Model Parameters
mlflow_url = os.environ['MLFLOWSERVER_URL']
ml_metric = 'metrics.Best_val_f1'
ml_exp = '[Pipeline IMDB] Training'
# Requesting 1 best model
mlflow.set_tracking_uri(mlflow_url)
mlflow.set_experiment(ml_exp)
df = mlflow.search_runs()
best_exp = df.loc[df[ml_metric].idxmax()]
run_id = best_exp['run_id']
print(run_id)
print("Best Model:", run_id) ## test1
logger.info("Best Model:"+str(run_id)) ##

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
    return jsonify({'response': "index page"+str(run_id)}), 201


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080)
