import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd

df = pd.read_csv(r'C:\Users\Hiroshi\PycharmProjects\job\plotly\data\at_ger_fct_msf_daily.csv',
                 index_col=[1], parse_dates=[1])
factor_col = [col for col in df.columns if 'FCT' in col]
factor_col.insert(0, 'Return')
df.loc[:, factor_col] = df.loc[:, factor_col].astype(float)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                suppress_callback_exceptions=True)

title = html.P('Factor Backtesting', style={'textAlign': 'center',
                                            'fontSize': 30})

nav = dbc.Nav(
        [
            dbc.NavLink("IC", href="/", active="exact"),
            dbc.NavLink("ITEM 2", href="/item-2", active="exact"),
            dbc.NavLink("ITEM 3", href="/item-3", active="exact"),
        ],
        pills=True, style={'margin': '0.3rem'}
    )

sidebar = html.Div([
    html.P('Factor', className='font-weight-bold font-italic',
           style={'fontSize': 20, 'margin': '1rem'}),
    dcc.Dropdown(id='my-fct-picker', multi=False, value='FCT_DE_TENURE',
                 options=[{'label': x, 'value': x}
                          for x in df.columns if 'FCT' in x]),
    html.Hr(),
    html.P('Universe', className='font-weight-bold font-italic',
           style={'fontSize': 20, 'margin': '1rem'}),
    dcc.Dropdown(id='my-univ-picker', multi=False, value='UNIV_MSCI_ACWI',
                 options=[{'label': x, 'value': x}
                          for x in df.columns if 'UNIV' in x]),
    html.Hr(),
    html.Button(id='my-button', n_clicks=0, children='apply')

])

sidebar2 = html.Div([
    html.P('SELECT UNIV or GRP', className='font-weight-bold font-italic',
           style={'fontSize': 20, 'margin': '1rem'}),
    dcc.Dropdown(id='select-group', multi=False, value='UNIV',
                 options=[{'label': 'UNIV', 'value': 'UNIV'},
                          {'label': 'GRP', 'value': 'GRP'}]),
    html.P(id='group-name', className='font-weight-bold font-italic',
           style={'fontSize': 20, 'margin': '1rem'}),
    dcc.Dropdown(id='group-items'),
    html.Hr(),
    html.P('TYPE UNIV or GRP or SOMETHING', className='font-weight-bold font-italic',
           style={'fontSize': 20, 'margin': '1rem'}),
    dbc.Input(id="type-group", placeholder="Type something...", type="text"),
    html.P(id='group-name-type', className='font-weight-bold font-italic',
           style={'fontSize': 20, 'margin': '1rem'}),
    dcc.Dropdown(id='group-items-type'),
])


sidebar3 = html.Div([])

page_sidebar = html.Div(id='page-sidebar', children=[])
page_content = html.Div(id='page-content', children=[])


app.layout = dbc.Container([
    dcc.Location(id="url"),
    dbc.Row([
        dbc.Col(title, width=4),
        dbc.Col(nav, width=8)
    ], className='bg-primary text-white', style={'height': '5vh'}),
    dbc.Row([
        dbc.Col(page_sidebar, width=4, className='bg-light'),
        dbc.Col(page_content, width=8)
    ], style={'height': '95vh'})
], fluid=True)


@app.callback(
    Output('page-sidebar', 'children'),
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return sidebar, [
            dcc.Graph(id='ic-cumulative', figure={}, style={'height': '47.5vh'}),
            dcc.Graph(id='ic-period', figure={}, style={'height': '47.5vh'})
        ]
    elif pathname == "/item-2":
        return sidebar2, [
            dcc.Graph(figure={}, style={'height': '47.5vh'}),
            dcc.Graph(figure={}, style={'height': '47.5vh'})
        ]
    elif pathname == "/item-3":
        return sidebar3, [
            dcc.Graph(figure={}, style={'height': '25vh'}),
            dcc.Graph(figure={}, style={'height': '70vh'})
        ]
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


@app.callback(Output('ic-cumulative', 'figure'),
              Input('my-button', 'n_clicks'),
              [State('my-fct-picker', 'value'),
               State('my-univ-picker', 'value')])
def update_ic(n_clicks, selected_fct, selected_univ):
    df_univ = df[df[selected_univ] == 1]
    df_fct = df_univ.loc[:, factor_col]
    ic = df_fct.groupby('Period').corr().unstack()[
        selected_fct]['Return'].cumsum()

    fig = {'data': [go.Scatter(x=ic.index,
                               y=ic,
                               name=selected_fct,
                               mode='lines+markers',
                               marker={'size': 5,
                                       'opacity': 0.5,
                                       'line': {'width': 0.5, 'color': 'white'}})],
           'layout': go.Layout(xaxis={'title': 'Date'},
                               yaxis={'title': 'Cumulative IC'},
                               hovermode='closest',
                               template='plotly',
                               margin={'l': 30, 'b': 30, 't': 30, 'r': 30},
                               showlegend=True,
                               legend=dict(
                                   yanchor="top",
                                   y=0.99,
                                   xanchor="left",
                                   x=0.01,
                                   bgcolor='rgba(0,0,0,0)'
                               )
                               )}
    return fig


@app.callback(Output('ic-period', 'figure'),
              Input('my-button', 'n_clicks'),
              [State('my-fct-picker', 'value'),
               State('my-univ-picker', 'value')])
def update_ic_period(n_clicks, selected_fct, selected_univ):
    df_univ = df[df[selected_univ] == 1]
    df_fct = df_univ.loc[:, factor_col]
    ic = df_fct.groupby('Period').corr().unstack()[
        selected_fct]['Return']
    ic_roll = ic.fillna(ic.mean()).rolling(36).mean()

    fig = {'data': [go.Bar(x=ic.index,
                           y=ic,
                           name="Average: " + str(ic.mean().round(2))),
                    go.Scatter(x=ic_roll.index,
                               y=ic_roll,
                               name='12 day moving average')],
           'layout': go.Layout(xaxis={'title': 'Date'},
                               yaxis={'title': 'Period IC'},
                               hovermode='closest',
                               template='plotly',
                               margin={'l': 30, 'b': 30, 't': 30, 'r': 30},
                               showlegend=True,
                               legend=dict(
                                   yanchor="top",
                                   y=0.99,
                                   xanchor="left",
                                   x=0.01,
                                   bgcolor='rgba(0,0,0,0)'
                               )
                               )}
    return fig


@app.callback(Output('group-items', 'options'),
              Output('group-items', 'value'),
              Output('group-name', 'children'),
              Input('select-group', 'value'))
def update_selector(selected_group):
    if selected_group == 'UNIV':
        return ([{'label': x, 'value': x} for x in df.columns if 'UNIV' in x],
                'UNIV_MSCI_ACWI',
                'UNIVERSE')
    else:
        return ([{'label': x, 'value': x} for x in df.columns if 'GRP' in x],
                'GRP_GICS_SEC',
                'GROUP')


@app.callback(Output('group-items-type', 'options'),
              Output('group-items-type', 'value'),
              Output('group-name-type', 'children'),
              Input('type-group', 'value'))
def update_selector(selected_group):
    if selected_group == 'UNIV':
        return ([{'label': x, 'value': x} for x in df.columns if 'UNIV' in x],
                'UNIV_MSCI_ACWI',
                'UNIVERSE')
    elif selected_group == 'GRP':
        return ([{'label': x, 'value': x} for x in df.columns if 'GRP' in x],
                'GRP_GICS_SEC',
                'GROUP')
    else:
        return ([{'label': 'OTHER', 'value': 'OTHER'}],
                'OTHER',
                'OTHER')


if __name__ == '__main__':
    app.run_server(debug=True, port=3000)
