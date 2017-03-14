import numpy as np
from pykalman import KalmanFilter

class PositionEstimator(object):
    def __init__(self):
        self.setup_kf()
        self.test_stream("")

    def setup_kf(self):
        self.dt = 0.012
        self.A = np.array([[1, self.dt, -self.dt**2/2], [0, 1, -self.dt], [0, 0, 1] ])
        self.C = np.array([1, self.dt, -self.dt**2/2])

        print self.A
        print self.C

    def update_kf(self):
        pass

    def test_stream(self, file):
        pass

if __name__ == "__main__":
    p = PositionEstimator()
