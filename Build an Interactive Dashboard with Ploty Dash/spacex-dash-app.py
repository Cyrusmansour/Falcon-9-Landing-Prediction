# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                    ],
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True
                                ),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: f'{i}' for i in range(0, 10001, 2500)},
                                    value=[min_payload, max_payload]
                                ),


                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Aggregate success counts by site
        df_all_sites = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(df_all_sites, 
                     names='Launch Site', 
                     title='Total Successful Launches by Site')
        return fig
    else:
        # Step 1: Filter the dataframe for the selected site
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        # Step 2: Extract 'class' column and count occurrences of 0 and 1
        class_counts = site_df['class'].value_counts().sort_index()  # sort_index to ensure 0 comes before 1

        # Step 3: Create a DataFrame for plotting
        pie_df = pd.DataFrame({
            'Outcome': ['Failure', 'Success'],
            'Count': [class_counts.get(0, 0), class_counts.get(1, 0)]  # .get to avoid KeyError if one class is missing
        })

        # Step 4: Generate the pie chart
        fig = px.pie(pie_df,
                    values='Count',
                    names='Outcome',
                    title=f'Success vs Failure Launches for site {entered_site}',
                    hole=0.4)

        fig.update_traces(marker=dict(colors=['red', 'green']))
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')])

def update_scatter_plot(entered_site, payload_range):
    # Unpack payload range from slider
    low, high = payload_range

    # Filter data by payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                             (spacex_df['Payload Mass (kg)'] <= high)]

    # Further filter by launch site if not ALL
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for all Sites')
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(site_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for {entered_site}')
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
