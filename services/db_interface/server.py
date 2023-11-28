from flask import Flask, request


app = Flask(__name__)


@app.route("/", methods=['GET'])
def route_index():
    return {'message': "Hello, World! This is 'db_interface'."}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
