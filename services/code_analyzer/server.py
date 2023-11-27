from flask import Flask, request
from code_analyzer import CodeAnalyzer


app = Flask(__name__)


@app.route("/", methods=['GET'])
def route_index():
    return {'message': "Hello, world!\n This is 'code_analyzer'."}, 200


@app.route("/analyze", methods=['GET'])
def route_analyze():
    if (data := request.get_json()) is None:
        return {'message': "no json body"}, 400
    if (code := data.get('code')) is None:
        return {'message': "no code"}, 400

    analyzer = CodeAnalyzer(code)
    analyzer.analyze()
    return analyzer.to_json(), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
