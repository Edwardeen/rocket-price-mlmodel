# Import required libraries
import pandas as pd
import dash
from dash import dcc, html  # Import dash components properly
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into a Pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),

    html.Br(),

    # Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),
    
    # Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={i: f"{i}" for i in range(int(min_payload), int(max_payload) + 1, 2000)},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # Scatter Plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback function for Pie Chart
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"),
)
def update_pie_chart(selected_site):
    if selected_site == "ALL":
        fig = px.pie(spacex_df, values='class', names='Launch Site', title="Total Success Launches for All Sites")
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_count = filtered_df['class'].value_counts().reset_index()
        success_count.columns = ['class', 'count']
        fig = px.pie(success_count, values='count', names='class', title=f"Success vs Failure for {selected_site}")
    return fig

# Callback function for Scatter Plot
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"), Input("payload-slider", "value")]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    if selected_site != "ALL":
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(
        filtered_df, x="Payload Mass (kg)", y="class",
        color="Booster Version Category",
        title="Payload vs. Success Rate"
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
