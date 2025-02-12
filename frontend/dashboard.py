from dash import dash, dcc, html, Input, Output
import requests
import pandas as pd
import plotly.express as px
import json
import os

# use config.json to get the url
# config_path = os.getenv("CONFIG_PATH", "config.json")
'''
with open("config.json", "r") as f:
    config = json.load(f)
url = config["backend_url"]
'''
url = "http://127.0.0.1:5050" # test
app = dash.Dash(__name__)



# user page
user_layout = html.Div([
    html.H2("User Electricity Consumption Page"),
    dcc.Input(id="user_id", type="text", placeholder="Input User ID", debounce=True),
    dcc.RadioItems(
        id="user_timeframe",
        options=[
            {"label": "Daily", "value": "day"},
            {"label": "Weekly", "value": "week"},
            {"label": "Monthly", "value": "month"},
        ],
        value="day",
        inline=True,
    ),
    html.Button("Fetch Data", id="fetch_user_data", n_clicks=0),
    dcc.Graph(id="user_chart")
])


# for user to register
register_layout = html.Div([
    html.H2("User Registration"),
    dcc.Input(id="register_username", type="text", placeholder="Enter Username", debounce=True),
    dcc.Dropdown(
        id="register_area",
        options=[ # just show these limited locations
            {"label": "Sentosa", "value": "Sentosa"},
            {"label": "Orchard Road", "value": "Orchard Road"},
            {"label": "Marina Bay", "value": "Marina Bay"},
            {"label": "Jurong Point", "value": "Jurong Point" }
        ],
        placeholder="Select Area"
    ),
    html.Button("Register", id="register_button", n_clicks=0),
    html.Div(id="register_status")
])


# admin page
admin_layout = html.Div([
    html.H2("Admin Page"),
    
    # Function 1: time range selection
    html.Div([
        html.Label("Select Time Range:"),
        dcc.DatePickerRange(
            id="date_picker_range",
            start_date="2024-12-29", # same as the date in simulate_request.py
            end_date="2025-1-10",
            display_format="YYYY-MM-DD",
            style={"marginBottom": "10px"}
        ),
    ]),

    # Function 2: time dimension selection
    dcc.RadioItems(
        id="admin_timeframe",
        # TODO: 我这里改了，值定义的是 D, W, M
        # OK
        options=[
            {"label": "Daily", "value": "D"},
            {"label": "Weekly", "value": "W"},
            {"label": "Monthly", "value": "M"},
        ],
        value="month",  # default to monthly dimension
        inline=True,
        style={"marginBottom": "20px"}
    ),
    
    # Function 3: area selection
    html.Div([
        html.Label("Select Area:"),
        dcc.Dropdown(
            id="admin_area_dropdown",
            options=[],  
            value="all",  # default value is all areas
            style={"marginBottom": "20px"}
        ),
    ]),
    
    dcc.Graph(id="admin_chart"),
    
    # Function 4: CSV Download button
    html.Button("Download CSV", id="download_csv", n_clicks=0),
    html.Div(id="admin_table")
])



# layout
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label="User", children=[user_layout]),
        dcc.Tab(label="User Register", children=[register_layout]),
        dcc.Tab(label="Admin", children=[admin_layout])
    ])
])



# User page callback
@app.callback(
    Output("user_chart", "figure"),
    Input("fetch_user_data", "n_clicks"),
    Input("user_id", "value"),
    Input("user_timeframe", "value")
)
def user_chart(n_clicks, user_id, timeframe):
    start_date = "2024-11-25 05:00:00"
    end_date = "2025-01-02 22:00:00"
    if not user_id:
        return px.line(title="Input User ID")

    response = requests.get(f"{url}/user/getData", params={"user_id": user_id})
    if response.status_code != 200:
        return px.line(title="Failed to get data.")
    
    data = response.json()
    
    if timeframe == "day":
        usage_history = data["day_usage_history"]
        time_range = pd.date_range(start=start_date, end=end_date, freq='D')
    elif timeframe == "week":
        usage_history = data["week_usage_history"]
        time_range = pd.date_range(start=start_date, end=end_date, freq='W')
    elif timeframe == "month":
        usage_history = data["month_usage_history"]
        time_range = pd.date_range(start=start_date, end=end_date, freq='M')
    else:
        return px.line(title="Invalid Timeframe")
    
    df = pd.DataFrame({timeframe: time_range[:len(usage_history)], "usage": usage_history})
    plot = px.bar(df, x=timeframe, y="usage", title=f"{data['username']}'s Electricity Consumption")
    # history data uses light blue, the latest data uses dark blue
    plot.update_traces(marker_color=["#ADD8E6"] * len(usage_history) + ["#4682B4"])
    # asked gpt how to display data in this following  style
    plot.update_traces(hovertemplate="<b>Time: </b>%{x}<br><b>Usage: </b>%{y}<br><extra></extra>")
    return plot



# callback for register
@app.callback(
    Output("register_status", "children"),
    Input("register_button", "n_clicks"),
    Input("register_username", "value"),
    Input("register_area", "value")
)
def register_user(n_clicks, username, area):
    if n_clicks > 0:
        if not username or not area:
            return "Please enter both username and select an area."
        
        response = requests.post(f"{url}/user/register", json={"username": username, "area": area})
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return f"Registration successful! Your User ID: {data['user_id']}"
            else:
                return f"Registration failed: {data.get('message', 'Unknown error')}"
        return "Server error. Please try again later."
    return ""



# Admin page callback
# when admin set the filter of areas and time demisions, then this callback will send the chosen filter to backend and get filtered data
# callback to get area data for admin
@app.callback(
    Output("admin_area_dropdown", "options"),
    Input("date_picker_range", "start_date"),
    Input("date_picker_range", "end_date"),
)
def get_area_options(start_date, end_date):
    # get all the available areas from backend data
    response = requests.get(f"{url}/admin/catalogue", params={"start_date": start_date, "end_date": end_date})
    # TODO: 我是根据app.py写上面的的api，可能要麻烦曹老爷你核对一下对不对
    # 这个可以了
    if response.status_code == 200:
        data = response.json()
        areas = data.get('area_set', [])
        return [{"label": area, "value": area} for area in areas]
    return []

# callback to get all data for admin
@app.callback(
    Output("admin_chart", "figure"),
    Output("admin_table", "children"),
    Input("date_picker_range", "start_date"),
    Input("date_picker_range", "end_date"),
    Input("admin_timeframe", "value"),
    Input("admin_area_dropdown", "value")
)
def admin_data(start_date, end_date, timeframe, area):
    print(start_date, end_date, timeframe, area)
    # Send the selected filters to the backend to get all the data
    response = requests.get(f"{url}/admin/getRaw", params={
        # TODO: 我是根据app.py写上面的的api，可能要麻烦曹老爷你核对一下对不对
        # 这里有个问题，你选完日期之后要组装时间 2024-11-25 00:00:00 -> 2025-01-02 23:59:59 这样，这个时间范围才是对的
        "start_date": start_date,
        "end_date": end_date,
        "timeframe": timeframe,
        "area": area
    })

    if response.status_code != 200:
        return px.bar(title="No data available"), "Error fetching data."

    data = response.json()
    df = pd.DataFrame(data)  # Assuming the response is a dict that can be converted to DataFrame
    
    # Plot the chart
    plot = px.bar(df, x="time", y="usage", title="Electricity Consumption by Area")
    
    # Table for previewing CSV data
    table = html.Table([
        html.Tr([html.Th(col) for col in df.columns])  # Headers
    ] + [
        html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(len(df))
    ])
    
    return plot, table

# Admin callback for CSV download
@app.callback(
    Output("download_csv", "href"),
    Input("download_csv", "n_clicks"),
    Input("date_picker_range", "start_date"),
    Input("date_picker_range", "end_date"),
    Input("admin_timeframe", "value"),
    Input("admin_area_dropdown", "value")
)
def download_csv(n_clicks, start_date, end_date, timeframe, area):
    if n_clicks > 0:
        # Request the filtered data from the backend
        response = requests.get(f"{url}/admin/getData", params={
            "start_date": start_date,
            "end_date": end_date,
            "timeframe": timeframe,
            "area": area
        })
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            
            # Return a link to download the CSV file
            return f"data:text/csv;charset=utf-8,{csv}"
        
    return ""  # If no CSV, return empty string



if __name__ == "__main__":
    app.run_server(debug=True)
