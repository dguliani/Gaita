import datetime
import time
import pandas as pd
import numpy as np

import constants as const

import plotly
plotly.tools.set_credentials_file(username=const.PY_USERNAME, api_key=const.PY_API_KEY)
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go

class Dashboard(object):
    def __init__(self):
        # self.create_step_stream()
        self.clear_stream()
        self.stream_random()
        # self.create_3d_cluster()

    def clear_stream(self):
        s1 = py.Stream(const.PY_STEPH_STREAM)
        s2 = py.Stream(const.PY_STEPL_STREAM)

        # We then open a connection
        s1.open()
        s2.open()

        s1.write(dict(x=[],y=[]))
        s2.write(dict(x=[],y=[]))

        s1.close()
        s2.close()

    def stream_random(self):
        print("Sending Random Data")
        # We will provide the stream link object the same token that's associated with the trace we wish to stream to
        s1 = py.Stream(const.PY_STEPH_STREAM)
        s2 = py.Stream(const.PY_STEPL_STREAM)

        # s = py.Stream(stream_id)

        # We then open a connection
        s1.open()
        s2.open()

        k = 5    # some shape parameter

        # Delay start of stream by 5 sec (time to switch tabs)
        time.sleep(2)
        j = 0
        for i in range(100):
            print j
            # Current time on x-axis, random numbers on y-axis
            x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            # y = (np.cos(k*i/50.)*np.cos(i/50.)+np.random.randn(1))[0]
            y1 = 0.7*np.sin(j)
            y2 = 0.3*np.sin(j)

            if y1 < 0:
                y1 = 0
                j = j+0.15
            if y2 < 0:
                y2 = 0

            # Send data to your plot
            s1.write(dict(x=x, y=y1))
            s2.write(dict(x=x, y=y2))

            #     Write numbers to stream to append current data on plot,
            #     write lists to overwrite existing data on plot
            j = j+0.7
            time.sleep(0.2)  # plot a point every second
        # Close the stream when done plotting
        s1.close()
        s2.close()

    def create_step_stream(self):
        print("Resetting Both Streams")
        stream_id1 = dict(token=const.PY_STEPH_STREAM, maxpoints=30)
        stream_id2 = dict(token=const.PY_STEPL_STREAM, maxpoints=30)

        trace_1 = go.Scatter(
            x=[],
            y=[],
            mode='',
            name ='Step Height',
            stream=stream_id1         # (!) embed stream id, 1 per trace
        )

        trace_2 = go.Scatter(
            x=[],
            y=[],
            mode='',
            name = 'Step Length',
            stream=stream_id2         # (!) embed stream id, 1 per trace
        )

        data = go.Data([trace_1, trace_2])

        # Add title to layout object
        layout = go.Layout(title='Live Steps',
                           xaxis=dict(title='Time'),
                           yaxis=dict(title='Distance (m)'))

        # Make a figure object
        fig = go.Figure(data=data, layout=layout)

        # Send fig to Plotly, initialize streaming plot, open new tab
        py.plot(fig, filename='Live Steps')

    def create_3d_cluster(self):
        df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/alpha_shape.csv')
        df.head()
        # print len(df['x'])
        # return
        scatter = dict(
            mode = "markers",
            name = "y",
            type = "scatter3d",
            x = (df['x']), y = (df['y']), z = (df['z']),
            marker = dict( size=2, color="rgb(23, 190, 207)" )
        )
        # clusters = dict(
        #     alphahull = 7,
        #     name = "y",
        #     opacity = 0.1,
        #     type = "mesh3d",
        #     x = df['x'], y = df['y'], z = df['z']
        # )
        layout = dict(
            title = 'Steps Clustered by Gait',
            scene = dict(
                xaxis = dict( zeroline=False, title="Step Height (m)" ),
                yaxis = dict( zeroline=False, title="Step Length (m)"),
                zaxis = dict( zeroline=False, title="Double Support (s)" ),
            )
        )
        fig = dict( data=[scatter], layout=layout )
        py.plot(fig, filename='Step Clustering')


if __name__=="__main__":
    d = Dashboard()