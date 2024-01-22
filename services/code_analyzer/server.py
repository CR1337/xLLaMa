from flask import Flask, request
from flask_cors import CORS
from code_analyzer import CodeAnalyzer
from code_extractor import CodeExtractor
from code_highlighter import CodeHighlighter
import os
from db_interface import DbInterface


app = Flask(__name__)
CORS(app)


@app.route("/", methods=['GET'])
def route_index():
    return {'message': "Hello, world!\n This is 'code_analyzer'."}, 200


@app.route("/analyze-prediction", methods=['GET'])
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


@app.route("/highlight", methods=['GET'])
def route_highlight():
    if (code_snippet_id := request.args.get('code_snippet')) is None:
        return {'message': "no code_snippet"}, 400

    if (clickable_class := request.args.get('clickable_class')) is None:
        return {'message': "no clickable_class"}, 400

    if (clickable_names := request.args.get('clickable_names')) is None:
        return {'message': "no clickable_names"}, 400
    clickable_names = clickable_names.split(',')
    print(clickable_names, flush=True)

    if (on_click_attribute := request.args.get('on_click_attribute')) is None:
        return {'message': "no on_click_attribute"}, 400

    if (click_handler_name := request.args.get('click_handler')) is None:
        return {'message': "no click_handler"}, 400

    code_snippet = DbInterface.get_code_snippet(code_snippet_id)
    code = code_snippet['code']

    return {
        "html": CodeHighlighter.highlight(
            code, clickable_names, clickable_class,
            on_click_attribute,  click_handler_name, code_snippet_id
        )
    }, 200


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('CODE_ANALYZER_INTERNAL_PORT')),
        debug=True
    )
