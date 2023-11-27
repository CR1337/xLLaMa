from flask import Flask, request, Request, Response
from llm_request import LlmRequest, OpenAiRequest, OllamaRequest
from config import Defaults
from openai import AuthenticationError

app = Flask(__name__)


class RequestError(Exception):

    http_code: int

    def __init__(self, message: str, http_code: int):
        self.message = message
        self.http_code = http_code
        super().__init__()


def _build_llm_request(request_: Request) -> LlmRequest:
    if (data := request_.get_json()) is None:
        raise RequestError("no json body", 400)
    if (model := data.get('model')) is None:
        raise RequestError("no model", 400)
    if (prompt := data.get('prompt')) is None:
        raise RequestError("no prompt", 400)

    system_prompt = data.get('system_prompt')
    repeat_penalty = data.get('repeat_penalty', Defaults.REPEAT_PENALTY)
    max_tokens = data.get('max_tokens', Defaults.MAX_TOKENS)
    seed = data.get('seed', Defaults.SEED)
    temperature = data.get('temperature', Defaults.TEMPERATURE)
    top_p = data.get('top_p', Defaults.TOP_P)
    stop = data.get('stop')

    if OllamaRequest.has_model(model):
        llm_request_class = OllamaRequest
    elif OpenAiRequest.has_model(model):
        llm_request_class = OpenAiRequest
    else:
        raise RequestError("model not available", 404)

    return llm_request_class(
        model,
        prompt,
        system_prompt,
        repeat_penalty,
        max_tokens,
        seed,
        temperature,
        top_p,
        stop
    )


@app.route('/', methods=['GET'])
def route_index():
    return {'message': "Hello, world! This is 'llm_facade'."}, 200


@app.route('/models', methods=['GET'])
def route_models():
    models = OllamaRequest.models()
    try:
        models += OpenAiRequest.models()
    except AuthenticationError:
        pass
    return {'models': models}, 200


@app.route("/install-model", methods=['GET'])
def route_install_model():
    model = request.get_json().get('model')
    if model is None:
        return {'error': 'no model'}, 400
    stream = request.get_json().get('stream', True)
    if stream:
        return Response(
            OllamaRequest.install_model(model, stream),
            mimetype='text/event-stream'
        )
    else:
        return OllamaRequest.install_model(model, stream)


@app.route('/generate', methods=['GET'])
def route_generate():
    try:
        llm_request = _build_llm_request(request)
    except RequestError as error:
        return {'message': error.message}, error.http_code
    else:
        llm_response = llm_request.generate()
        return llm_response.to_json(), 200


@app.route("/generate-stream", methods=['GET'])
def route_generate_stream():
    try:
        llm_request = _build_llm_request(request)
    except RequestError as error:
        return {'message': error.message}, error.http_code
    else:
        llm_response_stream = llm_request.generate_stream()
        return Response(
            llm_response_stream.sse_generator(),
            mimetype='text/event-stream'
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
