from dash import dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
from valfapp.app import app

layout = html.Div([
    html.H1("Sales Report"),
    dcc.Graph(id="sales-report-graph"),
    dcc.Dropdown(id="product-type-dropdown", options=[
        {"label": "Product A", "value": "product_a"},
        {"label": "Product B", "value": "product_b"},
        {"label": "Product C", "value": "product_c"},
    ], value="product_a")
])


@app.callback([Output("sales-report-graph", "figure"),
               [Input("product-type-dropdown", "value")]])
def update_graph(selected_product_type):
    if selected_product_type == "product_a":
        # generate data for product A
        x = [1, 2, 3]
        y = [4, 1, 2]
    elif selected_product_type == "product_b":
        # generate data for product B
        x = [1, 2, 3]
        y = [2, 4, 5]
    else:
        # generate data for product C
        x = [1, 2, 3]
        y = [5, 2, 3]

    return {
        "data": [
            {
                "x": x,
                "y": y,
                "type": "line",
                "name": selected_product_type
            },
            {
                "x": x,
                "y": y,
                "type": "candlestick",
                "name": selected_product_type
            }
        ],
        "layout": {
            "title": f"Sales for {selected_product_type}"
        }
    }

if __name__ == "__main__":
    app.run_server(debug=True)
