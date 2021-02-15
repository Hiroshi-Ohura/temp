import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd


df = pd.read_csv(
    r"C:\Users\Hiroshi\PycharmProjects\job\plotly\data\at_ger_fct_msf_daily.csv",
    index_col=[1], parse_dates=[1])

factor_col = [col for col in df.columns if 'FCT' in col]
# factor_col.insert(0, 'Identifier')
factor_col.insert(0, 'Return')

df.loc[:, factor_col] = df.loc[:, factor_col].astype(float)

fct_options = [
    {'label': col, 'value': col} for col in df.columns if 'FCT' in col]

fig2 = {'data': [go.Scatter(x=df.head(100)['Return'],
                            y=df.head(100)['FCT_DS_ACT_UT_QT'],
                            text=df.head(100)['Identifier'],
                            mode='markers',
                            marker={'size': 15,
                                    'opacity': 0.5,
                                    'line': {'width': 0.5, 'color': 'white'}})],
        'layout': go.Layout(title='Utilization',
                            xaxis={'title': 'Return'},
                            yaxis={'title': 'FCT_DS_ACT_UT_QT'},
                            hovermode='closest',
                            template='plotly_white')}

div_style3 = {
    'width': '40%',
    'height': 250,
    'backgroundColor': 'lime',
    'margin': '5%',
    'display': 'inline-block'
}

div_style4 = {
    'width': '29%',
    'height': 250,
    'backgroundColor': 'skyblue',
    'margin': '2%',
    'display': 'inline-block'
}

app = dash.Dash(__name__)

app.layout = html.Div([
    html.P('Factor Performance', style={
        'fontSize': 10,
        'color': 'white',
        'backgroundColor': '#000000',
        'width': 400,
        'margin': '5% auto',
        'display': 'inline-block',
    }),
    dcc.Tabs([
        dcc.Tab(label='IC', children=[
            html.Div([
                dcc.Dropdown(id='fct-picker',
                             options=fct_options,
                             value='FCT_DS_ACT_UT_QT'),
                html.Div([
                    dcc.Graph(id='ic_cumulative'),
                    dcc.Graph(id='ic_period')
                    ])
            ], style={'display', 'inline-block'}),
        ]),
        dcc.Tab(label='Cumulative Return', children=[
            dcc.Graph(
                figure=fig2
            )
        ]),
        dcc.Tab(label='Test', children=[
            html.Div([
                html.Div([
                    html.Div(style=div_style3),
                    html.Div(style=div_style3)
                ], id='first_leader'),
                html.Div([
                    html.Div(style=div_style4),
                    html.Div(style=div_style4),
                    html.Div(style=div_style4),
                ], id='second_leader')
            ], id='leader'

            )
        ])
    ])
])


@app.callback(Output('ic_cumulative', 'figure'),
              [Input('fct-picker', 'value')])
def update_ic(selected_fct):
    df_fct = df.loc[:, factor_col]
    ic = df_fct.groupby('Period').corr().unstack()[
        selected_fct]['Return'].cumsum()

    fig1 = {'data': [go.Scatter(x=ic.index,
                                y=ic,
                                mode='lines+markers',
                                marker={'size': 5,
                                        'opacity': 0.5,
                                        'line': {'width': 0.5, 'color': 'white'}})],
            'layout': go.Layout(title='Borrow Cost Score',
                                xaxis={'title': 'Return'},
                                yaxis={'title': 'FCT_COST_SCORE'},
                                hovermode='closest',
                                template='plotly')}
    return fig1


if __name__ == '__main__':
    app.run_server(debug=True)
