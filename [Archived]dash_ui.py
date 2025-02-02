from dash import Dash, html, dash_table, dcc, callback, Output, Input

app = Dash(__name__)

login_layout = [html.Div([
	html.H1("Hello!"),
	html.H2("You Are:")
]),
	dcc.Dropdown(id="Dropdown_Identity_selection", options=[
	             "User", "Admin"], value="User", clearable=False),
	html.Div(id='Input_user_id_container'),
	html.Button("Login", id="Login_button")
]

user_layout = [html.Div([
	html.H1("Hello!"),
	html.H2("You Are:")
])]

admin_layout = [html.Div([
	html.H1("Hello!"),
	html.H2("You Are:")
])]

# 根据是否时用户，判断是否要给User ID输入框


@app.callback(
	Output(component_id="Input_user_id_container", component_property="children"),
	Input(component_id="Dropdown_Identity_selection", component_property="value")
)
def choose_identity(value):
	if value == "User":
		return dcc.Input(id="Input_user_id", type="text", placeholder="User ID")
	else:
		return

# 登录


@app.callback(
	Input(component_id="Login_button", component_property="n_clicks"),
	prevent_initial_call=True
)
def login(n_clicks):
	pass


if __name__ == '__main__':
    app.run_server(debug=True)
