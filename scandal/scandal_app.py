from ast import literal_eval
from datetime import datetime
from flask import Flask
from flask import render_template, request

from hypatia import create_app
from hypatia.ingress.db import get_dataframe
from hypatia.analytics import tables as tbl
from hypatia.analytics.lin_reg_exp import experiment
from hypatia.ingress.cimis_api import get_active_stations
from hypatia.visualization import timeseries as ts

app = Flask(__name__)
app.config['DEBUG'] = True
app = create_app()


@app.route('/')
def index():
    return render_template('layout.html')


@app.route('/regression', methods=['GET'])
def regression():
    return render_template('regression.html',
                           features=tbl.all_cpu_features + tbl.all_dht_targets,
                           outputs=tbl.all_dht_targets)


@app.route('/predict_et', methods=['GET'])
def predict_et():
    return render_template('predict_et.html')


@app.route('/test_et_prediction', methods=['GET'])
def test_et_prediction():
    active_stations = get_active_stations()
    return render_template('test_et_prediction.html',
                           stations=active_stations)


@app.route('/predict_frost', methods=['GET'])
def predict_frost():
    return render_template('predict_frost.html')


@app.route('/test_et_prediction/submit', methods=['POST'])
def test_et_prediction_submit():
    return render_template('et_report.html')


@app.route('/predict_et/submit', methods=['POST'])
def predict_et_submit():
    return render_template('et_report.html')


@app.route('/regression/submit', methods=['POST'])
def regression_submit():
    features = request.form.getlist('features')
    features = [literal_eval(el) for el in features]
    target = literal_eval(request.form.get('output'))
    test_start = request.form.get('test_start_date')
    smoothing = 'smoothing' in request.form
    preprocessing = None
    if smoothing:
        window_size = int(request.form.get('window_size')) or tbl.WINDOW_SIZE
        preprocessing = [['sliding_window.rolling_mean', window_size]]
    pca = 'pca' in request.form
    if pca:
        dimensions = int(request.form.get('dimensions'))
    train_hours = tbl.HOURS_1_336
    test_hours = tbl.HOURS_1_336
    result_data = experiment(test_start=test_start, train_hours=train_hours,
                             test_hours=test_hours, features=features,
                             target=target, preprocessing=preprocessing)
    msg = 'Predicting {} from {} with the test starting on {}'.format(
        str(target), str(features), str(test_start))

    return render_template('regression_report.html', msg=msg,
                           data=result_data.to_html())


@app.route('/visualize', methods=['GET', 'POST'])
def visualize():
    inputs = tbl.all_tables  # all_table_names
    return render_template('visualization.html', inputs=inputs)


@app.route('/visualize/submit', methods=['POST'])
def visualize_submit():
    debug = True
    start = datetime.strptime(request.form.get('start'), tbl.TIME_FORMAT)
    end = datetime.strptime(request.form.get('end'), tbl.TIME_FORMAT)
    inputs = request.form.getlist('inputs')
    inputs = [literal_eval(el) for el in inputs]

    if debug:
        print(start, end, inputs)
    data = get_dataframe(inputs, start, end, debug=True)
    if debug:
        print(data.head())
    data = ts.ts_viz(data)

    return data


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True, debug=True)
