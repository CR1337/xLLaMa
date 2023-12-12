from flask import Flask, request, Response, Request
from flask_cors import CORS
from db_interface import DbInterface
import os
from typing import List, Type
from llm_request import (
    LlmRequest, OpenAiRequest, OllamaRequest, REQUEST_CLASSES
)


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

    for request_class in REQUEST_CLASSES:
        if request_class.has_model(llm['name']):
            llm_request_class: Type[LlmRequest] = request_class
            break
        else:
            raise RequestError("model not available", 400)

    return llm_request_class(
        repeat_penalty=request.args.get('repeat_penalty'),
        max_tokens=request.args.get('max_tokens'),
        seed=request.args.get('seed'),
        temperature=request.args.get('temperature'),
        top_p=request.args.get('top_p'),
        llm=llm_id,
        framework_item=request.args.get('framework_item'),
        system_prompt=request.args.get('system_prompt'),
        parent_follow_up=request.args.get('parent_follow_up'),
        prompt_parts=request.args.get('prompt_parts'),
        stop_sequences=request.args.get('stop_sequences')
    )


@app.route('/', methods=['GET'])
def route_index():
    return {'message': "Hello, world! This is 'llm_facade'."}, 200


@app.route('/models', methods=['GET', 'POST'])
def route_models():
    if request.method == 'GET':
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
            OllamaRequest.install_model_stream(model),
            mimetype='text/event-stream'
        )
    else:
        return OllamaRequest.install_model(model)


@app.route('/generate', methods=['GET'])
def route_generate():
    try:
        llm_request = build_llm_request(request)
    except RequestError as error:
        return {'message': error.message}, error.http_code
    else:
        if request.args.get('stream', True):
            return Response(
                llm_request.generate_stream(),
                mimetype='text/event-stream'
            )
        else:
            return llm_request.generate()


if __name__ == "__main__":
    persist_models()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get('LLM_FACADE_INTERNAL_PORT')),
        debug=True
    )
