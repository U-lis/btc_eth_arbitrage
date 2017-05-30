import logging

from chalice import Chalice

from monitor import BithumbMonitor, KorbitMonitor

logging.basicConfig(level=logging.INFO)

app = Chalice(app_name='arbitrage')


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/{str: currency}')
def monitor(currency: str):
    # data format: [[quantity, price], [...], ...]
    result = {}
    monitor_b = BithumbMonitor()




# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.json_body
#     # Suppose we had some 'db' object that we used to
#     # read/write from our database.
#     # user_id = db.create_user(user_as_json)
#     return {'user_id': user_id}
#
# See the README documentation for more examples.
#
