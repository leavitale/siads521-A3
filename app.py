import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

#Load file
car_emissions = pd.read_csv('Fuel_Consumption_2000-2022.csv')

#Drop NAs
car_emissions.dropna(axis = 1, how = 'all', inplace = True)
car_emissions.dropna(how = 'all', inplace = True)

#Make make, class and model lower
car_emissions.loc[:,'MAKE'] = car_emissions['MAKE'].str.lower()
car_emissions.loc[:,'VEHICLE CLASS'] = car_emissions['VEHICLE CLASS'].str.lower()
car_emissions.loc[:,'MODEL'] = car_emissions['MODEL'].str.lower()

# I create my title function
def set_title(plot):
    plot.layout.title.x = 0.5
    plot.layout.title.xanchor = 'center'
    plot.layout.title.font.size = 20
    return plot

# I create my plot functions
def make_line(g):
    if g.empty:
        return px.line(title="No data")
    line = px.line(g.groupby('YEAR', as_index=False)['EMISSIONS'].mean(), x='YEAR', y='EMISSIONS',
               title = '<b>Mean Emissions Over Time<b>')
    line.update_xaxes(dtick=1, tickformat="d")
    return set_title(line)

def make_bar(g):
    if g.empty:
        return px.bar(title="No data")
    bar = px.bar(g.groupby(['MAKE'], as_index=False)['EMISSIONS'].mean().sort_values(by=['EMISSIONS'], ascending=False),
           x='MAKE', y='EMISSIONS', title='<b>Mean Car Emissions By Make<b>')
    return set_title(bar)

def make_boxplot(g, dim = "FUEL"):
    if g.empty or dim not in g.columns:
        return px.box(title="No data")

    boxplot = px.box(g, x=dim, y='EMISSIONS', points = 'all', title=f'<b>Emissions by {dim.title()}<b>')

    if pd.api.types.is_numeric_dtype(g[dim]):
        values = np.sort(g[dim].dropna().unique())
        boxplot.update_xaxes(tickmode="array", tickvals=values, ticktext=[str(val) for val in values])

    return set_title(boxplot)

def make_treemap(g, brand):
    if g.empty:
        return px.treemap(title=f"No data for {brand}")
    agg_model = (g.groupby(['MAKE', 'MODEL'], as_index=False).agg(EMISSIONS=('EMISSIONS', 'mean'),
                                                                  owners = ('EMISSIONS', 'size')))
    treemap = px.treemap(agg_model, path=['MAKE', 'MODEL'], values='owners',
               color='EMISSIONS', color_continuous_scale='Greens', title=f'<b>Mean Model Emissions For {brand}<b>')
    return set_title(treemap)

# Create my Dash server
app = Dash()
server = app.server

yr_min, yr_max = int(car_emissions["YEAR"].min()), int(car_emissions["YEAR"].max())
default_brand = car_emissions['MAKE'].sort_values().iloc[0]

app.layout = html.Div([

    html.H1("Vehicle Emissions Dashboard", style={"textAlign": "center", "fontWeight":"bold"}),

    # I add the year slider
    html.Div([html.Label("Year Range"),
    dcc.RangeSlider(id = "years", min = yr_min, max = yr_max, value = [yr_min, yr_max],step = 1, allowCross = False, marks = None,
                              tooltip = {"placement":"bottom","always_visible":True}),],
             style = {"display":"inline-block", "width":"450px"}),

    # I add the brand widget for the treemap
    html.Div([html.Label("Treemap Brand"),
    dcc.Dropdown(id = "brand", options = car_emissions['MAKE'].drop_duplicates().sort_values(), value = default_brand,
                 placeholder = "Select a Brand for the Treemap"),], style = {"display":"inline-block", "width":"300px"}),

html.Div([html.Label("Boxplot Variable"),
    dcc.Dropdown(id = "dim", options = [
            {"label":"Fuel Type",     "value":"FUEL"},
            {"label":"Cylinders",     "value":"CYLINDERS"},
            {"label":"Make",          "value":"MAKE"},
            {"label":"Engine Size",   "value":"ENGINE SIZE"},
            {"label":"Vehicle Class", "value":"VEHICLE CLASS"},
            {"label":"Transmission",  "value":"TRANSMISSION"},
        ], value = "FUEL",
                 placeholder = "Select a variable for the boxplot"),], style = {"display":"inline-block", "width":"300px"}),

    # I add a line break before my plots
    html.Br(),

    # I add the plots

    html.Div([html.Div([dcc.Graph(id="line")], style={"width":"49%","display":"inline-block"}),
              html.Div([dcc.Graph(id="treemap")], style={"width":"49%","display":"inline-block"}),
              html.Div([dcc.Graph(id="bar")], style={"width":"49%","display":"inline-block"}),
              html.Div([dcc.Graph(id="boxplot")], style={"width":"49%","display":"inline-block"}),]),
])


@app.callback( Output("line","figure"),
               Output("treemap","figure"),
               Output("bar","figure"),
               Output("boxplot","figure"),
               Input("years","value"),
               Input("brand","value"),
               Input("dim","value"),
)

# I update the plots with the filters
def update_all(year_range, brand):
    # The dataset used will be filtered with the year slider
    y0, y1 = (yr_min, yr_max) if not year_range else (int(year_range[0]), int(year_range[1]))
    g = car_emissions[(car_emissions["YEAR"] >= y0) & (car_emissions["YEAR"] <= y1)]

    # I also filter the treemap by the brand selected
    g_treemap = g[g['MAKE'] == brand]

    return (
        make_line(g),
        make_treemap(g_treemap, brand),
        make_bar(g),
        make_boxplot(g, dim),
    )

# I run the dashboard
if __name__ == '__main__':
    app.run(debug=True)
