import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

#Load file
car_emissions = pd.read_csv('Fuel_Consumption_2000-2022.csv')

#Drop NAs
car_emissions.dropna(axis = 1, how = 'all', inplace = True)
car_emissions.dropna(how = 'all', inplace = True)

#Make make and class lower
car_emissions.loc[:,'MAKE'] = car_emissions['MAKE'].str.lower()
car_emissions.loc[:,'VEHICLE CLASS'] = car_emissions['VEHICLE CLASS'].str.lower()
car_emissions.loc[:,'MODEL'] = car_emissions['MODEL'].str.lower()

def make_line(g):
    if g.empty:
        return px.line(title="No data")
    return px.line(g.groupby('YEAR', as_index=False)['EMISSIONS'].mean(), x='YEAR', y='EMISSIONS',
               title = 'Mean Emissions Over Time')

def make_bar(g):
    if g.empty:
        return px.bar(title="No data")
    return px.bar(g.groupby(['MAKE'], as_index=False)['EMISSIONS'].mean(), x = 'MAKE', y = 'EMISSIONS', title = 'Mean Car Emissions By Make')

def make_scatter(g):
    if g.empty:
        return px.scatter(title="No data")
    return px.scatter(g, x = 'ENGINE SIZE', y = 'EMISSIONS', title = 'Emission by Engine Size')

def make_violin(g):
    if g.empty:
        return px.violin(title="No data")
    return px.violin(g, x = 'FUEL', y = 'EMISSIONS', title = 'Emission by Fuel Type')

def make_treemap(g):
    if g.empty:
        return px.treemap(title="No data")
    agg_model = g.groupby(['MAKE','MODEL'], as_index=False)['EMISSIONS'].mean()
    return px.treemap(agg_model, path=['MAKE','MODEL'], values='EMISSIONS', title = 'Mean Model Emissions For Bugatti')

app = Dash()
server = app.server

yr_min, yr_max = int(car_emissions["YEAR"].min()), int(car_emissions["YEAR"].max())

app.layout = html.Div([
    dcc.RangeSlider(id="years", min=yr_min, max=yr_max, value=[yr_min, yr_max],
                    step=1, allowCross=False, marks=None,
                    tooltip={"placement":"bottom","always_visible":True}),
    html.Div([
        html.Div([dcc.Graph(id="line")], style={"width":"49%","display":"inline-block"}),
        html.Div([dcc.Graph(id="treemap")], style={"width":"49%","display":"inline-block"}),
    ]),
    html.Div([
        html.Div([dcc.Graph(id="bar")], style={"width":"49%","display":"inline-block"}),
        html.Div([dcc.Graph(id="violin")], style={"width":"49%","display":"inline-block"}),
        html.Div([dcc.Graph(id="scatter")], style={"width":"49%","display":"inline-block"}),
    ]),
])


@app.callback(
    Output("line","figure"),
    Output("treemap","figure"),
    Output("bar","figure"),
    Output("violin","figure"),
    Output("scatter","figure"),
    Input("years","value"),
)
def update_all(year_range):
    y0, y1 = (yr_min, yr_max) if not year_range else (int(year_range[0]), int(year_range[1]))
    g = car_emissions[(car_emissions["YEAR"] >= y0) & (car_emissions["YEAR"] <= y1)]
    return (
        make_line(g),
        make_treemap(g),
        make_bar(g),
        make_violin(g),
        make_scatter(g)
    )

if __name__ == '__main__':
    app.run(debug=True)
