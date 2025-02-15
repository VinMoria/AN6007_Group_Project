from dash import dash, dcc, html, Input, Output
import requests
import pandas as pd
import plotly.express as px
import json
import os

# use config.json to get the url
# config_path = os.getenv("CONFIG_PATH", "config.json")

with open("config.json", "r") as f:
    config = json.load(f)
url = config["backend_url"]
# 下面这个只用于我测试这个dashboard，实际应该是上面三行代码取消注释，下面这行url注释掉
# 别用这个了，你测试的时候也用config，就是python运行的话要先cd frontend
# url = "http://127.0.0.1:33468" # test
app = dash.Dash(__name__)



# user page
user_layout = html.Div([
    html.H2("User Electricity Consumption Page"),
    dcc.Input(id="user_id", type="text", placeholder="Input User ID", debounce=True),
    dcc.RadioItems(
        id="user_timeframe",
        options=[
            {"label": "Detail", "value": "detail"},
            {"label": "Daily", "value": "day"},
            {"label": "Weekly", "value": "week"},
            {"label": "Monthly", "value": "month"}

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



# layout
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label="User", children=[user_layout]),
        dcc.Tab(label="User Register", children=[register_layout])
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
    if not user_id:
        return px.line(title="Input User ID")

    response = requests.get(f"{url}/user/getData", params={"user_id": user_id})
    if response.status_code != 200:
        return px.line(title="Failed to get data.")
    
    data = response.json()
    
    if timeframe == "day":
        usage_history = data["day_usage_history"]
    elif timeframe == "week":
        usage_history = data["week_usage_history"]
    elif timeframe == "month":
        usage_history = data["month_usage_history"]
    elif timeframe == "detail":
        usage_history = data["day_detail_usage_history"]
    else:
        return px.line(title="Invalid Timeframe")
    
    # 将二维数组转换为DataFrame
    df = pd.DataFrame(usage_history, columns=["date", "usage"])
    
    plot = px.bar(df, x="date", y="usage", title=f"{data['username']}'s Electricity Consumption")
    # history data uses light blue
    plot.update_traces(marker_color="#ADD8E6")
    # 保持原有的hover样式
    plot.update_traces(hovertemplate="<b>Time: </b>%{x}<br><b>Usage: </b>%{y}<br><extra></extra>")
    # 设置X轴为分类轴，保持字符串格式
    plot.update_xaxes(type='category')
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



if __name__ == "__main__":
    app.run_server(debug=True)
