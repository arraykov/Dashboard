from flask import Flask, redirect, request, render_template, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from cefpage import register_callbacks, generate_page_1
from prefpage import generate_table_page_2
import warnings
from datetime import timedelta
import psycopg2
import os
warnings.filterwarnings('ignore')

# Flask app and login setup
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') 
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=14)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def get_db_connection():
    dbname = os.environ.get('DB_NAME')
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    host = os.environ.get('DB_HOST')

    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    return conn

users = {'user@example.com': {'password': 'pass'}}

class User(UserMixin):
    def __init__(self, email):
        self.id = email

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = True if request.form.get('remember') else False

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password_hash = %s", (email, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            login_user(User(email), remember=remember)
            return redirect('/main/cefs')
        else:
            return 'Invalid credentials'
    return render_template('login.html')

# Dash app setup
external_stylesheets = [dbc.themes.BOOTSTRAP]
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/main/', suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)

dash_app.layout = html.Div([
    dbc.Navbar(
        [
            dbc.NavbarBrand(html.Img(src='assets/logo.png', height="30px"), href="/main/cefs"),
            dbc.Container(
                [
                    dbc.Nav([
                        dbc.NavLink("Closed-End Funds", href="/main/cefs", className="nav-link"),
                        dbc.NavLink("Preferred Stocks", href="/main/preferreds", className="nav-link"),
                        dbc.NavLink("Market Overview", href="/main/markets", className="nav-link")
                    ], className="ml-auto", navbar=True)
                ]
            )
        ],
        className="navbar navbar-expand-lg navbar-dark bg-dark hidden-navbar"
    ),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@dash_app.callback(Output('page-content', 'children'),
                   [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/main/preferreds':
        return generate_table_page_2()  # Content for Page 2
    elif pathname == '/main/markets':
        return html.Div("Work In Progress")  # Content for Page 3
    elif pathname == '/main/cefs':
        return generate_page_1()  # Content for Page 1 (Default landing page after login)
    else:
        # Redirect or show a default page if the pathname doesn't match
        return "Page not found"  # Or redirect to a default page

register_callbacks(dash_app)

if __name__ == '__main__':
    app.run(debug=False)
