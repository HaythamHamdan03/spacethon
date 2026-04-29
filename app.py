from flask import Flask, jsonify, render_template
import json

app = Flask(__name__)

# Load results once when server starts
with open('results_v2.json', 'r') as f:
    results = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    return jsonify(results)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)