import os
import numpy as np
import torch
import mlflow

import warnings, logging
import subprocess
import requests

from flask import Flask, jsonify, request
from flask import current_app, abort, Response

import json
# from json import JSONEncoder

## Logger, App, Device config
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
application = Flask(__name__)
device = torch.device('cpu')
## mlflow config
mlflow_url = os.environ['MLFLOWSERVER_URL']
mlflow.set_tracking_uri(mlflow_url)
mlflow.set_registry_uri(mlflow_url)


## init deployed model dict
models = dict()



def request_model_run_id(ml_exp:str, ml_metric:str) -> str:
    ## Request best model run_id by exp and metric
    mlflow.set_experiment(ml_exp)
    df = mlflow.search_runs()
    best_exp = df.loc[df[ml_metric].idxmax()]
    run_id = best_exp['run_id']
    logger.info("Requesting Best Model of [exp:%s] by [metric:%s]: run id %s"%(ml_exp, ml_metric, str(run_id)))
    return run_id


def deploy_model(ml_exp:str, ml_metric:str, model_name:str) -> str:
    ## Deploy and name the best model of a given metric in an exp
    run_id = request_model_run_id(ml_exp, ml_metric)
    loaded_model = mlflow.pytorch.load_model('runs:/%s/pytorch-model'%run_id).to(device)
    ## Add the best model to models dict
    new_deploy = {model_name: [loaded_model, ml_exp, ml_metric]}
    models.update(new_deploy)
    resp = "Model %s deployed successfully"%model_name
    return resp
    
    
def call_model(input_data, model):
    preds = model(*input_data)
    return np.argmax(preds["logits"].cpu().numpy(), axis=1) # turn one-hot prediction score to class




@application.route('/')
def index():
    logger.info('Visited index page')
    return jsonify({'response': "index page"}), 201


## Debug and run bash commands
@application.route('/raw', methods=['POST'])
def raw():
    # Read inputs/classes or Return reason of abort
    if not request.json \
    or not 'command' in request.json:
        abort(400)
    response = os.popen(request.json['command']).read().strip()
    logger.info('Visited raw page with bash command: \n%s'%request.json['command'])
    return jsonify({'response': response}), 201


## Deploy models (download them and save in a dict)
@application.route('/deploy', methods=['POST'])
def deploy():
    # Read inputs/classes or Return reason of abort
    if not request.json \
    or not 'exp' in request.json \
    or not 'metric' in request.json \
    or not 'model_name' in request.json:
        abort(400)
    logger.info('-- DEPLOY function called --')
    exp = request.json['exp']
    metric = request.json['metric']
    model_name = request.json['model_name']
    resp = deploy_model(exp, metric, model_name)
    logger.info(resp)
    return jsonify({'response': resp}), 201


## Deploy models (download them and save in a dict)
@application.route('/remove', methods=['POST'])
def remove():
    # Read inputs/classes or Return reason of abort
    if not request.json \
    or not 'model_name' in request.json:
        abort(400)
    logger.info('-- REMOVE function called --')
    model_name = request.json['model_name']
    del models[request.json['model_name']]
    resp = "Model %s removed successfully. Currently deployed models are: %s"%(model_name, ' '.join(list(models.keys())))
    logger.info(resp)
    return jsonify({'response': resp}), 201


## Predict
@application.route('/predict', methods=['POST'])
def predict():
    # Read inputs/classes or Return reason of abort
    if not request.json \
    or not 'model' in request.json \
    or not 'data' in request.json:
        abort(400)
    logger.info('-- PREDICT function called --')
    model = request.json['model']
    data = request.json['data']
    data = [torch.from_numpy(np.asarray(d)) for d in data]
    # decoded = json.loads(request.json)
    pred_output = call_model(data, models[model][0])
    logger.info(str(pred_output))
    return jsonify({'response': pred_output}), 201


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080)
