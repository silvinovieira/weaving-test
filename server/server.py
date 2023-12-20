"""
Server that will process the data from the pictures and the fabric movement.
"""

from flask import Flask, request, make_response


app = Flask(__name__)


@app.route('/pictures_batch', methods=['POST'])
def pictures_batch():
    if request.method == 'POST':
        print('Received pictures batch request')
        response = make_response()
        response.status_code = 201

        return response


@app.route('/surface_movement', methods=['POST'])
def surface_movement():
    if request.method == 'POST':
        print('Received surface movement request')

        response = make_response()
        response.status_code = 201

        return response


@app.route('/ping', methods=['GET'])
def ping():
    if request.method == 'GET':
        print('Received ping request')

        response = make_response()
        response.status_code = 204

        return response


def main() -> None:

    app.run(host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()
