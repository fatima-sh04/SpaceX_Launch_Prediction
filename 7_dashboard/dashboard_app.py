# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data CSV file
spacex_df = pd.read_csv(r"C:\Users\HP\Documents\SpaceX  Falcon 9 first stage Landing Prediction\spacex_launch_dash.csv")

# Get max and min payload for slider
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create dynamic slider marks based on payload range
step_size = 2500
slider_marks = {int(i): f'{int(i)}' for i in range(int(min_payload), int(max_payload)+step_size, step_size)}

# Create dynamic dropdown options from dataset launch sites
launch_sites = [{'label': 'All Sites', 'value': 'ALL'}]
launch_sites += [{'label': site, 'value': site} for site in sorted(spacex_df['Launch Site'].unique())]

# Create a Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),
    
    # Dropdown for Launch Site
    dcc.Dropdown(
        id='site-dropdown',
        options=launch_sites,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # Payload RangeSlider
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks=slider_marks,
        value=[min_payload, max_payload]
    ),

    # Scatter plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        df_grouped = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(df_grouped,
                     names='Launch Site',
                     values='class',
                     title='Total Successful Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = filtered_df['class'].value_counts().reset_index()
        counts.columns = ['class', 'count']
        fig = px.pie(counts,
                     values='count',
                     names='class',
                     title=f'Success vs Failure for site {selected_site}')
    return fig

# Callback for scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site == 'ALL':
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for All Sites')
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(site_df, 
                         x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for site {selected_site}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
