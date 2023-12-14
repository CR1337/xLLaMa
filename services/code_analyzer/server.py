from flask import Flask, request
from code_analyzer import CodeAnalyzer
from code_extractor import CodeExtractor
import os
from db_interface import DbInterface


app = Flask(__name__)


@app.route("/", methods=['GET'])
def route_index():
    return {'message': "Hello, world!\n This is 'code_analyzer'."}, 200


@app.route("/analyze-prediction", methods=['POST'])
def route_analyze_prediction():
    if (prediction_id := request.args.get('prediction')) is None:
        return {'message': "no prediction_id"}, 400

    prediction = DbInterface.get_prediction(prediction_id)

    extractor = CodeExtractor(prediction['text'])
    extractor.extract()

    code_snippet_ids = []
    for code_snippet in extractor.code_snippets:
        analyzer = CodeAnalyzer(code_snippet)
        analyzer.analyze()
        code_snippet_id = DbInterface.persist_code_snippet(
            code_snippet, analyzer, prediction_id
        )
        code_snippet_ids.append(code_snippet_id)
    return {"code_snippets": code_snippet_ids}, 200


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('CODE_ANALYZER_INTERNAL_PORT')),
        debug=True
    )
