### Import Packages ###
import dash
import dash_bootstrap_components as dbc

### Dash instance ###
app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.SLATE],
        )

if __name__ == "__main__":
    app.run(debug=True)
