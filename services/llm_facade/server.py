from flask import Flask, request, Response, Request
from flask_cors import CORS
from db_interface import DbInterface
import os
from typing import List, Type
from llm_request import LlmRequest
from openai_request import OpenAiRequest
from ollama_request import OllamaRequest


app = Flask(__name__)
CORS(app)


class RequestError(Exception):

    http_code: int

    def __init__(self, message: str, http_code: int):
        self.message = message
        self.http_code = http_code
        super().__init__()


def get_model_names() -> List[str]:
    model_names = OllamaRequest.model_names()
    if OpenAiRequest.available:
        model_names += OpenAiRequest.model_names()
    return model_names


def persist_models():
    persisted_models = DbInterface.llm_names()
    for model in get_model_names():
        if model not in persisted_models:
            DbInterface.post_llm(model)


def build_llm_request(request: Request) -> LlmRequest:
    llm_id = request.args.get('model')
    if llm_id is None:
        raise RequestError("no model", 400)
    llm = DbInterface.get_llm(llm_id)

    for request_class in [OllamaRequest, OpenAiRequest]:
        if llm['name'] in request_class.model_names():
            llm_request_class: Type[LlmRequest] = request_class
            break
        else:
            raise RequestError("model not available", 400)

    prompt_parts = request.args.get('prompt_parts')
    if prompt_parts is not None:
        prompt_parts = prompt_parts.split(',')

    stop_sequences = request.args.get('stop_sequences')
    if stop_sequences is not None:
        stop_sequences = stop_sequences.split(',')

    return llm_request_class(
        repeat_penalty=request.args.get('repeat_penalty'),
        max_tokens=request.args.get('max_tokens'),
        seed=request.args.get('seed'),
        temperature=request.args.get('temperature'),
        top_p=request.args.get('top_p'),
        llm_id=llm_id,
        framework_item_id=request.args.get('framework_item'),
        system_prompt_id=request.args.get('system_prompt'),
        parent_follow_up_id=request.args.get('parent_follow_up'),
        prompt_part_ids=prompt_parts,
        stop_sequence_ids=stop_sequences,
    )


@app.route('/', methods=['GET'])
def route_index():
    return {'message': "Hello, world! This is 'llm_facade'."}, 200


@app.route('/models', methods=['GET'])
def route_models():
    if request.method == 'GET':
        persist_models()
        return {'models': get_model_names()}, 200


@app.route("/models/install", methods=['GET'])
def route_install_model():
    model = request.args.get('model')
    if model is None:
        return {'message': 'no model'}, 400
    stream = request.args.get('stream', True)
    if model not in get_model_names():
        DbInterface.post_llm(model)
    if stream:
        return Response(
            OllamaRequest.install_model(model, stream),
            mimetype='text/event-stream'
        )
    else:
        return OllamaRequest.install_model(model, stream)


@app.route('/models/uninstall', methods=['GET'])
def route_uninstall_model():
    model = request.args.get('model')
    if model is None:
        return {'message': 'no model'}, 400
    if model in get_model_names():
        OllamaRequest.uninstall_model(model)
        DbInterface.delete_llm(model)
        return {}, 200
    else:
        return {'message': 'model not installed'}, 400


@app.route('/generate', methods=['GET'])
def route_generate():
    try:
        llm_request = build_llm_request(request)
    except RequestError as error:
        return {'message': error.message}, error.http_code
    else:
        stream = request.args.get('stream', True) in (
            'true', 'True', True, '1'
        )
        if stream:
            response = Response(
                llm_request.generate(stream),
                mimetype='text/event-stream'
            )
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['Connection'] = 'keep-alive'
            return response
        else:
            return llm_request.generate(stream)


@app.route('/ollama/instances', methods=['GET'])
def route_ollama_instances():
    return {'instances': OllamaRequest.OLLAMA_INSTANCES}, 200


if __name__ == "__main__":
    persist_models()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get('LLM_FACADE_INTERNAL_PORT')),
        debug=True
    )
