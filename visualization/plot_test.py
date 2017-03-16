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

import threading
import csv

class Dashboard(object):
    def __init__(self):
        self.create_step_stream()
        self.create_angle_stream()
        self.create_pressure_map()
        time.sleep(const.PY_STANDARD_DELAY)

        self.clear_all_streams()
        self.threads = []

        f_path = "/Users/dguliani/Documents/Development/workspace/Gaita/postprocessing/Processed/dynamic_05_03_17_shahid_walk_flat.csv"
        stream_thread = threading.Thread(target=self.stream_from_file, args=(f_path,))
        self.threads.append(stream_thread)
        stream_thread.start()

        stream_thread.join()
        self.threads.remove(stream_thread)
        # self.stream_from_file(f_path)


    def clear_all_streams(self):
        print "Clearing All Streams"
        s1 = py.Stream(const.PY_STEPH_STREAM)
        s2 = py.Stream(const.PY_STEPL_STREAM)
        s3 = py.Stream(const.PY_STEPA_STREAM)
        s4 = py.Stream(const.PY_PRESS_STREAM)
        # We then open a connection
        s1.open()
        s2.open()
        s3.open()
        s4.open()

        s1.write(dict(x=[],y=[]))
        s2.write(dict(x=[],y=[]))
        s3.write(dict(x=[],y=[]))
        s4.write(dict(x=[],y=[]))

        s1.close()
        s2.close()
        s3.close()
        s4.close()

        time.sleep(const.PY_STANDARD_DELAY)

    def stream_from_file(self, f_path):
        s1 = py.Stream(const.PY_STEPH_STREAM)
        s2 = py.Stream(const.PY_PRESS_STREAM)
        s3 = py.Stream(const.PY_STEPA_STREAM)

        s1.open()
        s2.open()
        s3.open()

        k = 5    # some shape parameter

        with open(f_path, 'rb') as csvfile:
            print ("Opened file")
            spamreader = csv.reader(csvfile)
            # row_count = sum(1 for row in spamreader)
            count = 0
            print "reading rows"
            for row in spamreader:
                if count is not 0:
                    t = float(row[0])
                    step_length = float(row[1])
                    step_height = float(row[2])
                    pitch = float(row[3])
                    fsr_frontl = float(row[4])*const.PY_PRESS_MULTIPLIER
                    fsr_back = float(row[5])*const.PY_PRESS_MULTIPLIER
                    fsr_frontr = float(row[6])*const.PY_PRESS_MULTIPLIER


                    s1.write(dict(x=t, y=step_height))
                    s3.write(dict(x=t, y=pitch))
                    trace = dict(x=[-1,0,1], y=[8,3,8],
                                 marker=dict(
                                     size = [fsr_frontl,fsr_back,fsr_frontr],
                                 )
                    )
                    s2.write(trace)

                    time.sleep(t - last_t)

                    if t > 15:
                        "Stopping stream after 60 seconds"
                        break

                last_t = float(row[0])
                count = count + 1

        s1.close()
        s2.close()
        s3.close()
        print f_path

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

    def create_pressure_map(self):
        print("Creating Pressure Map")
        stream_id = dict(token=const.PY_PRESS_STREAM, maxpoints=5)

        trace = go.Scatter(
            x=[-1,0,1],
            y=[8,3,8],
            mode='markers',
            name = 'Step Length',
            marker=dict(
                size = [10,40,10],
                color = 'red',
            ),
            stream=stream_id
        )

        data = go.Data([trace])

        # Add title to layout object
        layout = go.Layout(title='Live Pressure Map',
                           xaxis=dict(title='x',
                                      range=[-4, 4],
                                      showline=False,
                                      showgrid=False,
                                      zeroline=False,
                                      showticklabels=False),
                           yaxis=dict(title='y',
                                      range=[0,12],
                                      showline=False,
                                      showgrid=False,
                                      zeroline=False,
                                      showticklabels=False))

        # Make a figure object
        fig = go.Figure(data=data, layout=layout)

        # Send fig to Plotly, initialize streaming plot, open new tab
        py.plot(fig, filename='Live Pressure Map')

    def create_step_stream(self):
        print("Creating Step Height and Length Streams")
        stream_id1 = dict(token=const.PY_STEPH_STREAM, maxpoints=500)
        stream_id2 = dict(token=const.PY_STEPL_STREAM, maxpoints=500)

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
        layout = go.Layout(title='Live Step Height',
                           xaxis=dict(title='Time'),
                           yaxis=dict(title='Step Height (m)'))

        # Make a figure object
        fig = go.Figure(data=data, layout=layout)

        # Send fig to Plotly, initialize streaming plot, open new tab
        py.plot(fig, filename='Live Step Parameters')

    def create_angle_stream(self):
        print("Creating Step Angle Streams")
        stream_id = dict(token=const.PY_STEPA_STREAM, maxpoints=500)

        trace = go.Scatter(
            x=[],
            y=[],
            mode='',
            name ='Foot Angle',
            stream=stream_id         # (!) embed stream id, 1 per trace
        )


        data = go.Data([trace])

        # Add title to layout object
        layout = go.Layout(title='Live Foot Angle',
                           xaxis=dict(title='Time [s]'),
                           yaxis=dict(title='Foot Angle (Pitch) [deg]'))

        # Make a figure object
        fig = go.Figure(data=data, layout=layout)

        # Send fig to Plotly, initialize streaming plot, open new tab
        py.plot(fig, filename='Live Step Angles')

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