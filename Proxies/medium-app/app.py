from flask import Flask, jsonify
import sys

app = Flask(__name__)

@app.route('/')
def medium():
    if len(sys.argv) < 2:
        return 'Error'
    x = 0
    for i in range(100000000):
        x += i
    return 'Hello from ' + sys.argv[1] + ' in Medium. Computation result = ' + str(x) + "\n"

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=5001)