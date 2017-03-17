print('Hello')

import constants as const

import plotly
plotly.tools.set_credentials_file(username=const.PY_USERNAME, api_key=const.PY_API_KEY)
import plotly.plotly as py
import plotly.graph_objs as go

plotly.tools.set_credentials_file(username='biobit', api_key='6uOiEPcxqqmIxIaBADtz')

x = ['1', '2', '3', '4']
y = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16']

#       x0    x1    x2    x3    x4
z = [[0.00, 0.00, 0.00, 0.00],  # y0
     [0.00, 0.00, 0.00, 0.00],  # y1
     [0.00, 0.75, 0.75, 0.00],  # y2
     [0.75, 0.75, 0.75, 0.75],  # y3
     [0.75, 0.75, 0.75, 0.75],  # y4
     [0.75, 0.75, 0.75, 0.75],  # y5
     [0.00, 0.75, 0.75, 0.00],  # y6
     [0.00, 0.00, 0.00, 0.00],  # y7
     [0.30, 0.30, 0.30, 0.30],  # y8
     [0.00, 0.00, 0.00, 0.00],  # y9
     [0.00, 0.00, 0.00, 0.00],  # y10
     [0.00, 0.75, 0.75, 0.00],  # y11
     [0.00, 0.75, 0.75, 0.00],  # y12
     [0.00, 0.75, 0.75, 0.00],  # y13
     [0.00, 0.75, 0.75, 0.00],  # y14
     [0.00, 0.00, 0.00, 0.00]]  # y15

# annotations = []
# for n, row in enumerate(z):
#     for m, val in enumerate(row):
#         var = z[n][m]
#         annotations.append(
#             dict(
#                 text=str(val),
#                 x=x[m], y=y[n],
#                 xref='x1', yref='y1',
#                 font=dict(color='white' if val > 0.5 else 'white'),
#                 showarrow=False)
#             )

colorscale = [[0, '#428bca'], [0.5, '#ffcc5c'], [1, '#d9534f']]  # custom colorscale
trace = go.Heatmap(x=x, y=y, z=z, colorscale=colorscale, showscale=False)

fig = go.Figure(data=[trace])
fig['layout'].update(
    title="Foot Pressure Map",
    xaxis=dict(ticks='', side='top'),
    # ticksuffix is a workaround to add a bit of padding
    yaxis=dict(ticks='', ticksuffix='  '),
    width=700,
    height=700,
    autosize=False
)
py.plot(fig, filename='Foot Pressure Map', height=750)