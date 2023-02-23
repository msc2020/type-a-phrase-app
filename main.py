from waitress import serve

from implementations import *

if __name__ == '__main__':
    serve(app)
    #serve(app, host="0.0.0.0", port=8080)