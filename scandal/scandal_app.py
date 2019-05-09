from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/visualize', methods=['GET', 'POST'])
def visualize():
    return render_template('visualization.html')