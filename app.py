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

# I create my plot functions
def make_line(g):
    if g.empty:
        return px.line(title="No data")
    return px.line(g.groupby('YEAR', as_index=False)['EMISSIONS'].mean(), x='YEAR', y='EMISSIONS',
               title = 'Mean Emissions Over Time')

def make_bar(g):
    if g.empty:
        return px.bar(title="No data")
    return px.bar(g.groupby(['MAKE'], as_index=False)['EMISSIONS'].mean().sort_values(by=['EMISSIONS'], ascending=False),
                  x = 'MAKE', y = 'EMISSIONS', title = 'Mean Car Emissions By Make')

def make_scatter(g):
    if g.empty:
        return px.scatter(title="No data")
    return px.scatter(g, x = 'ENGINE SIZE', y = 'EMISSIONS', title = 'Emission by Engine Size')

def make_violin(g):
    if g.empty:
        return px.violin(title="No data")
    return px.violin(g, x = 'FUEL', y = 'EMISSIONS', title = 'Emission by Fuel Type')

def make_treemap(g, brand):
    if g.empty:
        return px.treemap(title=f"No data for {brand}")
    agg_model = g.groupby(['MAKE','MODEL'], as_index=False)['EMISSIONS'].mean()
    return px.treemap(agg_model, path=['MAKE','MODEL'], values='EMISSIONS', title = f'Mean Model Emissions For {brand}')


# Create my Dash server
app = Dash()
server = app.server

yr_min, yr_max = int(car_emissions["YEAR"].min()), int(car_emissions["YEAR"].max())
default_brand = 'dodge' if 'dodge' in car_emissions['MAKE'].sort_values() else car_emissions['MAKE'].sort_values().iloc[0]

app.layout = html.Div([

    # I add the year slider
    dcc.RangeSlider(id = "years", min = yr_min, max = yr_max, value = [yr_min, yr_max],
                    step = 1, allowCross = False, marks = None,
                    tooltip = {"placement":"bottom","always_visible":True}),

    # I add the brand widget for the treemap
    dcc.Dropdown(id = "brand", options = car_emissions['MAKE'].sort_values(), value = default_brand,
                 placeholder = "Select a Brand for the Treemap"),

    # I add the plots
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


@app.callback( Output("line","figure"),
               Output("treemap","figure"),
               Output("bar","figure"),
               Output("violin","figure"),
               Output("scatter","figure"),
               Input("years","value"),
               Input("brand","value"),
)

# I update the plots with the filters
def update_all(year_range, brand):
    # The dataset used will be filtered with the year slider
    y0, y1 = (yr_min, yr_max) if not year_range else (int(year_range[0]), int(year_range[1]))
    g = car_emissions[(car_emissions["YEAR"] >= y0) & (car_emissions["YEAR"] <= y1)]

    # I also filter the treemap by the brand selected
    g_treemap = g[g['MAKE'] == brand]
    # I add a clause so that if the year range makes it that the brand not have data, an empty treemap is returned
    #treemap = make_treemap(g_treemap, brand) if not g_treemap.empty else

    return (
        make_line(g),
        make_treemap(g_treemap, brand),
        make_bar(g),
        make_violin(g),
        make_scatter(g)
    )

# I run the dashboard
if __name__ == '__main__':
    app.run(debug=True)
