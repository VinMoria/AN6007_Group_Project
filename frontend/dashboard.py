from dash import dash, dcc, html, Input, Output
import requests
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__)
url = "http://127.0.0.1:1145"

# user page
user_layout = html.Div([
    html.H2("User Electricity Consumption Page"),
    dcc.Input(id="user_id", type="text", placeholder="Input User ID", debounce=True),
    dcc.RadioItems(
        id="user_timeframe",
        options=[
            {"label": "Dayly", "value": "day"},
            {"label": "Weekly", "value": "week"},
            {"label": "Monthly", "value": "month"},
        ],
        value="day",
        inline=True,
    ),
    html.Button("Fetch Data", id="fetch_user_data", n_clicks=0),
    dcc.Graph(id="user_chart")
])

# Admin page
admin_layout = html.Div([
    html.H2("Admin Page"),
    dcc.RadioItems(
        id="admin_timeframe",
        options=[
            {"label": "Dayly", "value": "day"},
            {"label": "Weekly", "value": "week"},
            {"label": "Monthly", "value": "month"},
        ],
        value="day",
        inline=True,
    ),
    html.Button("Get Data", id="fetch_admin_data", n_clicks=0),
    html.Button("Download CSV", id="download_csv", n_clicks=0),
    dcc.Graph(id="admin_chart"),
    html.Div(id="admin_table")
])

# set layout
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label="User", children=[user_layout]),
        dcc.Tab(label="Admin", children=[admin_layout])
    ])
])

# In the user page, draw line plots
@app.callback(
    Output("user_chart", "figure"),
    Input("fetch_user_data", "n_clicks"),
    Input("user_id", "value"),
    Input("user_timeframe", "value")
)
def user_chart(user_id, timeframe):
    if not user_id:
        return px.line(title="Input User ID")

    response = requests.get(f"{url}/user/getData", params={"user_id": user_id})
    if response.status_code != 200:
        return px.line(title="Fail to get data.")

    data = response.json()
    usage_history = data[f"{timeframe}_usage_history"]

    df = pd.DataFrame({timeframe: range(len(usage_history)), "usage": usage_history})
    plot = px.line(df, x=timeframe, y="usage", title=f"{data['username']}'s Electricity Consumption Data")
    return plot

if __name__ == "__main__":
    app.run_server(debug=True)
