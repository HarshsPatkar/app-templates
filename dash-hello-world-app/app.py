import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc

from databricks import sql
from databricks.sdk import WorkspaceClient


# --------------------------------------------------
# Configuration
# --------------------------------------------------

APP_NAME = "hello-smart"

CATALOG = "hello_smart_test"
SCHEMA = "activity"
TABLE = "app_activity"

# Replace this with your SQL Warehouse HTTP path
HTTP_PATH = "/sql/1.0/warehouses/c5dc2f05534d53d3"


# --------------------------------------------------
# Databricks connection
# --------------------------------------------------

w = WorkspaceClient()


def record_activity():
    """Record the latest App activity."""

    conn = sql.connect(
        server_hostname=w.config.host,
        http_path=HTTP_PATH,
        credentials_provider=lambda: w.config.authenticate,
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE {CATALOG}.{SCHEMA}.{TABLE}
                SET last_activity = current_timestamp()
                WHERE app_name = '{APP_NAME}'
                """
            )

        print("Activity recorded successfully")

    except Exception as e:
        print(f"Failed to record activity: {e}")

    finally:
        conn.close()


# --------------------------------------------------
# Dash App
# --------------------------------------------------

dash_app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)


# --------------------------------------------------
# Record activity whenever App receives a request
# --------------------------------------------------

@dash_app.server.before_request
def track_activity():
    record_activity()


# --------------------------------------------------
# Existing sample data
# --------------------------------------------------

chart_data = pd.DataFrame({
    'x': [x for x in range(30)],
    'y': [2 ** x for x in range(30)]
})


# --------------------------------------------------
# Existing App layout
# --------------------------------------------------

dash_app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H1('Hello world!!!'),
            width=12
        )
    ]),

    dcc.Graph(
        id='fare-scatter',
        figure=px.scatter(
            chart_data,
            x='x',
            y='y',
            labels={
                'x': 'Apps',
                'y': 'Fun with data'
            },
            template='simple_white'
        ),
        style={
            'height': '500px',
            'width': f'{min(100 + 50 * 30, 1000)}px'
        }
    )

], fluid=True)


# --------------------------------------------------
# Start App
# --------------------------------------------------

if __name__ == '__main__':
    dash_app.run(
        host='0.0.0.0',
        port=8000,
        debug=False
    )
