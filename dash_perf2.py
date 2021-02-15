import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd


df = pd.read_csv(
    r"C:\Users\Hiroshi\PycharmProjects\job\plotly\data\at_ger_fct_msf_daily.csv",
    index_col=[1], parse_dates=[1])

factor_col = [col for col in df.columns if 'FCT' in col]
factor_col.insert(0, 'Return')

df.loc[:, factor_col] = df.loc[:, factor_col].astype(float)

fct_options = [
    {'label': col, 'value': col} for col in df.columns if 'FCT' in col]
univ_options = [
    {'label': col, 'value': col} for col in df.columns if 'UNIV' in col]

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.P('Factor', style={'fontSize': 20}),
            dcc.Dropdown(id='fct-picker',
                         options=fct_options,
                         value='FCT_DS_ACT_UT_QT'),
            html.P('Universe', style={'fontSize': 20}),
            dcc.Dropdown(id='univ-picker',
                         options=univ_options,
                         value='UNIV_MSCI_ACWI'),
            html.Button(id='my-button', n_clicks=0, children='apply')
        ], style={'width': '20%', 'display': 'inline-block',
                  'verticalAlign': 'top', 'textAlign': 'left'}),
        html.Div([
            dcc.Graph(id='ic_cumulative'),
            dcc.Graph(id='ic_period')
        ], style={'width': '60%', 'display': 'inline-block'})
    ])
])


@app.callback(Output('ic_cumulative', 'figure'),
              Input('my-button', 'n_clicks'),
              [State('fct-picker', 'value'),
               State('univ-picker', 'value')])
def update_ic(n_clicks, selected_fct, selected_univ):
    df_univ = df[df[selected_univ] == 1]
    df_fct = df_univ.loc[:, factor_col]
    ic = df_fct.groupby('Period').corr().unstack()[
        selected_fct]['Return'].cumsum()

    fig = {'data': [go.Scatter(x=ic.index,
                               y=ic,
                               mode='lines+markers',
                               marker={'size': 5,
                                       'opacity': 0.5,
                                       'line': {'width': 0.5, 'color': 'white'}})],
           'layout': go.Layout(title=selected_fct,
                               xaxis={'title': 'Date'},
                               yaxis={'title': 'Cumulative IC'},
                               hovermode='closest',
                               template='plotly')}
    return fig


@app.callback(Output('ic_period', 'figure'),
              Input('my-button', 'n_clicks'),
              [State('fct-picker', 'value'),
               State('univ-picker', 'value')])
def update_ic_period(n_clicks, selected_fct, selected_univ):
    df_univ = df[df[selected_univ] == 1]
    df_fct = df_univ.loc[:, factor_col]
    ic = df_fct.groupby('Period').corr().unstack()[
        selected_fct]['Return']

    fig = {'data': [go.Bar(x=ic.index,
                           y=ic)],
           'layout': go.Layout(title=selected_fct,
                               xaxis={'title': 'Date'},
                               yaxis={'title': 'Cumulative IC'},
                               hovermode='closest',
                               template='plotly')}
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
