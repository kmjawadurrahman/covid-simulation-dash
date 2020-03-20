from datetime import datetime as dt
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div('Total deaths as of today:'),
    dcc.Input(
            id="total-deaths", type="number",
            debounce=False, value=1, min=1, max=100000
        ),
    html.Div('Fatality rate (%):'),
    dcc.Input(
            id="fatality-rate", type="number",
            debounce=False, value=2, min=0.1, max=100
        ),
    html.Div('Days from infection to death:'),
    dcc.Input(
            id="days-death", type="number",
            debounce=False, value=17.3, min=1, max=100
        ),
    html.Div('Case doubling time in days:'),
    dcc.Input(
            id="doubling-time", type="number",
            debounce=False, value=6.18, min=1, max=50
        ),
    html.Div('Number of vacant hospital beds available:'),
    dcc.Input(
            id="num-beds", type="number",
            debounce=False, value=50000, min=50, max=1000000
        ),
    html.Div('Number of ICUs available:'),
    dcc.Input(
            id="num-icus", type="number",
            debounce=False, value=10000, min=1, max=500000
        ),
    html.Div('Number of ventilators available:'),
    dcc.Input(
            id="num-ventilators", type="number",
            debounce=False, value=2000, min=1, max=100000
        ),
    html.Button(id='submit-button', n_clicks=0, children='Run Simulation'),
    html.Div(id='datatable-div'),
])

@app.callback(
    Output('datatable-div', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('total-deaths', 'value'),
     State('fatality-rate', 'value'),
     State('days-death', 'value'),
     State('doubling-time', 'value')])
def update_calc_table(n_clicks, total_deaths, fatality_rate,
                        days_death, doubling_time):
    number_cases_causing_death = round(total_deaths / (fatality_rate/100))
    number_times_cases_doubled = round(days_death / doubling_time, 2)
    true_cases_today = round(number_cases_causing_death * 2**number_times_cases_doubled)
    likely_true_cases_tomorrow = round(true_cases_today * 2**(1 / number_times_cases_doubled))
    likely_true_cases_ina_week = round(true_cases_today * 2**(7 / number_times_cases_doubled))
    likely_new_cases_tomorrow = likely_true_cases_tomorrow - true_cases_today
    likely_new_cases_ina_week = likely_true_cases_ina_week - true_cases_today
    return dash_table.DataTable(
                id='table',
                style_header={
                    'fontWeight': 'bold'
                },
                columns=[{"name": i, "id": i} for i in ['Calculated metric names', 'Calculated metric values']],
                data=[{'Calculated metric names': 'Number of cases that caused the deaths',
                        'Calculated metric values': number_cases_causing_death},
                        {'Calculated metric names': 'Number of times cases have doubled',
                                'Calculated metric values': number_times_cases_doubled},
                        {'Calculated metric names': 'True cases today',
                                'Calculated metric values': true_cases_today},
                        {'Calculated metric names': 'Likely true cases tomorrow',
                                'Calculated metric values': likely_true_cases_tomorrow},
                        {'Calculated metric names': 'Likely true cases in a week',
                                'Calculated metric values': likely_true_cases_ina_week},
                        {'Calculated metric names': 'Likely new cases tomorrow',
                                'Calculated metric values': likely_new_cases_tomorrow},
                        {'Calculated metric names': 'Likely new cases in a week',
                                'Calculated metric values': likely_new_cases_ina_week}])


if __name__ == '__main__':
    app.run_server(debug=True)
