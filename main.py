# layouyt =[dcc.Dropdown(id="costcenter1",
#                       className='dropdown-style',
#                       options=[{"label": cc, "value": cc} for cc in costcenters],
#                       multi=False,
#                       value="CNC",
#                       ),
# dbc.Graph(id='line_graph')
#
# ]
#
#
#
#
# df = ag.runquer("select - from ıasprdorder")
#
#
# @app.Callback(
#     Input("costcenter1",type=dropdown),
#     Output("line_graph",type=figure)
# )
# def costcentertolayout(costcenter):
#     df = df.loc[df["COSTCENTER"] = costcenter]
#     return px.line(data = df)
