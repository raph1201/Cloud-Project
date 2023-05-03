from flask import Flask, jsonify
import sys

app = Flask(__name__)

@app.route('/')
def light():
    if len(sys.argv) < 2:
        return 'Error'

    return 'Hello from ' + sys.argv[1] + ' in Light!\n'

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=5000)