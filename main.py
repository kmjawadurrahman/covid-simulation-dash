from datetime import datetime as dt
from datetime import timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd
import numpy as np
import plotly.graph_objects as go

external_stylesheets = ['https://storage.googleapis.com/sql_database_towhid/dash.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Div('Total deaths as of today:',
                        style={'margin-bottom': 3, 'font-weight': 'bold'}),
                dcc.Input(
                        id="total-deaths", type="number",
                        debounce=False, value=2, min=1, max=100000),
                html.Div('Fatality rate (%):',
                        style={'margin-bottom': 3, 'margin-top': 15,
                            'font-weight': 'bold'}),
                dcc.Input(
                        id="fatality-rate", type="number",
                        debounce=False, value=5, min=0.1, max=100),
                html.Div('Days from infection to death:',
                        style={'margin-bottom': 3, 'margin-top': 15,
                            'font-weight': 'bold'}),
                dcc.Input(
                        id="days-death", type="number",
                        debounce=False, value=17.3, min=1, max=100),
                html.Div('Case doubling time in days:',
                        style={'margin-bottom': 3, 'margin-top': 15,
                            'font-weight': 'bold'}),
                dcc.Input(
                        id="doubling-time", type="number",
                        debounce=False, value=6.18, min=1, max=50),
                html.Div('Hospital beds capacity:',
                        style={'margin-bottom': 3, 'font-weight': 'bold'}),
                dcc.Input(
                        id="num-beds", type="number",
                        debounce=False, value=50000, min=50, max=1000000),
                html.Div('ICU capacity:',
                        style={'margin-bottom': 3, 'margin-top': 15,
                            'font-weight': 'bold'}),
                dcc.Input(
                        id="num-icus", type="number",
                        debounce=False, value=10000, min=1, max=500000),
                html.Div('Ventilators capacity:',
                        style={'margin-bottom': 3, 'margin-top': 15,
                            'font-weight': 'bold'}),
                dcc.Input(
                        id="num-ventilators", type="number",
                        debounce=False, value=1000, min=1, max=100000),
                html.Div('% of cases requiring hospitalization:',
                        style={'margin-bottom': 3, 'margin-top': 15,
                            'font-weight': 'bold'}),
                dcc.Input(
                        id="pct-hospitalization", type="number",
                        debounce=False, value=20, min=1, max=50),
                html.Div('% of cases requiring ICU:',
                        style={'margin-bottom': 3, 'margin-top': 15,
                            'font-weight': 'bold'}),
                dcc.Input(
                        id="pct-icu", type="number",
                        debounce=False, value=5, min=0.5, max=20),
                html.Div('% of cases requiring hospitalization:',
                        style={'margin-bottom': 3, 'margin-top': 15,
                            'font-weight': 'bold'}),
                dcc.Input(
                        id="pct-ventilator", type="number",
                        debounce=False, value=1, min=0.1, max=10),
                html.Div('Simulate for next N days:',
                        style={'margin-bottom': 3, 'margin-top': 15,
                            'font-weight': 'bold'}),
                html.Div(
                    dcc.Input(
                            id="sim-days", type="number",
                            debounce=False, value=30, min=3, max=90
                    ), style={'margin-bottom': 30}),
                html.Button(id='submit-button', n_clicks=0, children='Run Simulation',
                        style={'margin-bottom': 0}),
                ], className='row', style=dict(fontSize=14)),
        ], className='two columns'),
        html.Div([
            html.Div([
                html.Div(id='barcharts-div')
            ], className='row')
        ], className='nine columns'),
    ], className='row'),
    html.Div([
        html.Div([
            html.Div(id='datatable-div')
        ], className='five columns'),
        html.Div([
            dcc.Markdown('''
            ###### Notes:
            - This simulation is based on the analysis done in this article: [Link to article](https://medium.com/@tomaspueyo/coronavirus-act-today-or-people-will-die-f4d3d9cd99ca)
            - It is known that there is a lag time before an infection gets reported as a confirmed case. So, a simulation model based on total number of deaths at present, fatality rate, days from infection to death, and case doubling rate has been used to estimate the actual true cases at present day.
            - Number of cases that caused the deaths = Total deaths as of today / (Fatality rate (in %) / 100)
            - Number of times cases have doubled = Days from infection to death / Case doubling time
            - True cases today = Number of cases that caused the deaths \* 2^(Number of times cases have doubled)
            - True cases on Nth day from today = True cases today \* 2^(Nth day number / Number of times cases have doubled)
            - The default values of fatality rate, days from infection to death, and case doubling rate are sensible defaults determined by studies on actual data (more details in the article linked above), but feel free to tweak these values as well.
            - Number of cases requiring hospitalizations, ICUs, ventilators have been adjusted by subtracting number of new cases from 10 days prior to account for cases that leave the hospital either due to recovery or death.
            - Note that this is a very simple model that makes a lot of assumptions. Also, this model only shows the outbreak scenarios without accounting for containment, mitigation or other phases of intervention. Hence, the graphs only show infinitely increasing trends. However, this simulation (especially for N<=30 days) gives you an idea about how and when your hospital capacities might be pushed to their limits.
            ''')
        ], className='six columns', style={'margin-left': '5%'}),
    ], className='row', style={'margin-top': 20}),
], className='eleven columns', style={'margin-top': 50, 'margin-bottom': 100,
    'margin-left': '7.5%'})

def calc_metrics(total_deaths, fatality_rate, days_death, doubling_time):
    number_cases_causing_death = round(total_deaths / (fatality_rate/100))
    number_times_cases_doubled = round(days_death / doubling_time, 2)
    true_cases_today = round(number_cases_causing_death * 2**number_times_cases_doubled)

    return (number_cases_causing_death, number_times_cases_doubled,
            true_cases_today)

def plot_barline_combo(case_factor, true_cases_list, dates_list, num_capacity,
                        bar_name, line_name, chart_title):
    num_cases_list = [round(case_factor*i) for i in true_cases_list]
    lag_dates_list = [i+timedelta(10) for i in dates_list]
    num_cases_arr = np.array(num_cases_list)
    num_new_cases_arr = np.array(num_cases_list[1:]+[0]) - num_cases_arr
    num_new_cases_arr = np.append(num_new_cases_arr[:-1], num_new_cases_arr[-1])
    num_cases_arr[10:] = num_cases_arr[10:] - num_new_cases_arr[:-10]
    bar_colors_list = ['#636efa' for _ in range(len(lag_dates_list))]
    crossed_indicator = False
    date_crossed = "-"
    for bar_idx in range(len(lag_dates_list)):
        if num_cases_arr[bar_idx] > num_capacity:
            bar_colors_list[bar_idx] = '#db1313'
            if not crossed_indicator:
                date_crossed = lag_dates_list[bar_idx]
                crossed_indicator = True

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=lag_dates_list,
            y=num_cases_arr,
            name=bar_name,
            marker_color=bar_colors_list
        )
    )
    fig.add_trace(
        go.Scatter(
            x=lag_dates_list,
            y=[num_capacity for _ in range(len(dates_list))],
            name=line_name
        )
    )
    annotations = []
    annotations.append(dict(xref='paper', x=0.65, y=num_capacity,
                                  xanchor='right', yanchor='bottom',
                                  text='{} = {}'.format(line_name, num_capacity),
                                  font=dict(family='Arial',
                                            size=12),
                                  showarrow=False))
    fig.update_layout(title={
                        'text': '<b>{}</b>'.format(chart_title),
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': {'size': 12}},
                   yaxis_title={'text': bar_name, 'font': {'size': 12}},
                   transition=dict(duration=1000),
                   showlegend=False,
                   annotations=annotations,
                   margin=dict(l=50,r=30,b=50,t=90))
    return fig, date_crossed

@app.callback(
    Output('datatable-div', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('total-deaths', 'value'),
     State('fatality-rate', 'value'),
     State('days-death', 'value'),
     State('doubling-time', 'value')])
def update_calc_table(n_clicks, total_deaths, fatality_rate,
                        days_death, doubling_time):
    number_cases_causing_death, \
    number_times_cases_doubled, \
    true_cases_today = \
        calc_metrics(total_deaths, fatality_rate, days_death, doubling_time)
    likely_true_cases_tomorrow = round(true_cases_today * 2**(1 / number_times_cases_doubled))
    likely_true_cases_ina_week = round(true_cases_today * 2**(7 / number_times_cases_doubled))
    likely_new_cases_tomorrow = likely_true_cases_tomorrow - true_cases_today
    likely_new_cases_ina_week = likely_true_cases_ina_week - true_cases_today
    return dash_table.DataTable(
                id='table',
                style_as_list_view=True,
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold',
                    'font-size': 12,
                },
                style_cell={'font-size': 12},
                columns=[{"name": i, "id": i} for i in ['Calculated metric names', 'Calculated metric values']],
                style_data_conditional=[
                    {
                        'if': {
                            'column_id': 'Calculated metric values',
                        },
                        'font-size': 16,
                    }],
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

@app.callback(
    Output('barcharts-div', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('total-deaths', 'value'),
     State('fatality-rate', 'value'),
     State('days-death', 'value'),
     State('doubling-time', 'value'),
     State('num-beds', 'value'),
     State('num-icus', 'value'),
     State('num-ventilators', 'value'),
     State('sim-days', 'value'),
     State('pct-hospitalization', 'value'),
     State('pct-icu', 'value'),
     State('pct-ventilator', 'value')])
def update_bar_charts(n_clicks, total_deaths, fatality_rate, days_death, doubling_time,
                        num_beds, num_icus, num_ventilators, sim_days,
                        pct_hospitalization, pct_icu, pct_ventilator):
    number_cases_causing_death, \
    number_times_cases_doubled, \
    true_cases_today = \
        calc_metrics(total_deaths, fatality_rate, days_death, doubling_time)
    date_today = dt.now().date()
    dates_list = [date_today]
    true_cases_list = [true_cases_today]

    for day_num in range(1, sim_days+1):
        true_cases_list.append(round(true_cases_today * 2**(day_num / number_times_cases_doubled)))
        dates_list.append(date_today+timedelta(day_num))

    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=dates_list,
            y=true_cases_list,
            line=dict(width=2),
            mode='lines+markers'
        )
    )
    fig1.update_layout(title={
                        'text': '<b>Estimation of true number of cases over time</b>',
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': {'size': 12}},
                   yaxis_title={'text': 'Estimated true number of cases', 'font': {'size': 12}},
                   transition={'duration': 1000},
                   margin=dict(l=50,r=30,b=50,t=90))

    fig2, date_crossed2 = plot_barline_combo(pct_hospitalization/100, true_cases_list, dates_list, num_beds,
                            'Estimated number of hospitalizations needed',
                            'Hospital beds capacity',
                            'Estimation of number of cases requiring hospitalization<br>(assuming on average 20% require hospitalization<br>10 days after infection)')

    fig3, date_crossed3 = plot_barline_combo(pct_icu/100, true_cases_list, dates_list, num_icus,
                            'Estimated number of ICUs needed',
                            'ICU capacity',
                            'Estimation of number of cases requiring ICUs<br>(assuming on average 5% require ICU<br>10 days after infection)')

    fig4, date_crossed4 = plot_barline_combo(pct_ventilator/100, true_cases_list, dates_list, num_ventilators,
                            'Estimated number of ventilators needed',
                            'Ventilators capacity',
                            'Estimation of number of cases requiring Ventilators<br>(assuming on average 1% require ventilators<br>10 days after infection)')

    html_div_children = [
        html.Div([
            html.Div([
                html.Div('Hospital bed shortage likely on:',
                    className='row', style=dict(fontWeight='bold', 
                            textAlign='left', marginLeft='5%', fontSize=14)),
                html.Div(str(date_crossed2), className='row',
                    style={'color':'red', 'font-size':24, 'text-align':'left', 'margin-left':'5%'}),
            ], className='four columns'),
            html.Div([
                html.Div('ICU shortage likely on:',
                    className='row', style=dict(fontWeight='bold',
                            textAlign='center', fontSize=14)),
                html.Div(str(date_crossed3), className='row',
                    style={'color':'red', 'font-size':24, 'text-align':'center'}),
            ], className='four columns'),
            html.Div([
                html.Div('Ventilator shortage likely on:',
                    className='row', style=dict(fontWeight='bold',
                            textAlign='right', marginRight='7%', fontSize=14)),
                html.Div(str(date_crossed4), className='row',
                    style={'color':'red', 'font-size':24, 'text-align':'right', 'margin-right':'7%'}),
            ], className='four columns'),
        ], className='row'),
        html.Div([
            html.Div([
                dcc.Graph(figure=fig1, id='totals-estimate',
                    config={"displayModeBar": False})
            ], className='six columns'),
            html.Div([
                dcc.Graph(figure=fig2, id='hospitalizations-estimate',
                    config={"displayModeBar": False})
            ], className='six columns'),
        ], className='row'),
        html.Div([
            html.Div([
                dcc.Graph(figure=fig3, id='icus-estimate',
                    config={"displayModeBar": False})
            ], className='six columns'),
            html.Div([
                dcc.Graph(figure=fig4, id='ventilators-estimate',
                    config={"displayModeBar": False})
            ], className='six columns'),
        ], className='row'),
    ]
    return html_div_children

if __name__ == '__main__':
    app.run_server(debug=False)
