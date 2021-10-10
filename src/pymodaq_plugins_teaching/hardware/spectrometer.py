import numpy as np
from pymodaq.daq_utils.daq_utils import gauss1D

class Spectrometer:

    axis = ['lambda0']
    Nactuators = len(axis)
    Nx = 256

    def __init__(self, positions=[632.], noise=0.1, amp=10, wh=20):
        super().__init__()
        if positions is None:
            self.current_positions = dict(zip(self.axis, [0. for ind in range(self.Nactuators)]))
        else:
            assert isinstance(positions, list)
            assert len(positions) == self.Nactuators
            self.current_positions = positions

        self._amp = amp
        self._noise = noise
        self._wh = wh

    @property
    def amplitude(self):
        return self._amp

    @amplitude.setter
    def amplitude(self, value):
        if value > 0.:
            self._amp = value

    @property
    def noise(self):
        return self._noise

    @noise.setter
    def noise(self, value):
        if value > 0.:
            self._noise = value

    @property
    def width(self):
        return self._wh

    @width.setter
    def width(self, value):
        if value > 0.:
            self._wh = value


    def check_position(self, axis):
        return self.current_positions[axis]

    def move_abs(self, position, axis):
        self.current_positions[axis] = position

    def move_rel(self, position, axis):
        self.current_positions[axis] += position

    def get_xaxis(self):
        return (np.linspace(0, self.Nx, self.Nx, endpoint=False) - self.Nx / 2) * 0.25 +\
               self.current_positions['lambda0']

    def set_Mock_data(self):
        """
        """
        x_axis = self.get_xaxis()
        return self._amp * gauss1D(x_axis, self.current_positions['H'], self._wh) +\
               self._noise * np.random.rand(self.Nx)

    def get_data_output(self, data=None):
        """
        Return generated data (2D gaussian) transformed depending on the parameters
        Parameters
        ----------
        data: (ndarray) data as outputed by set_Mock_data

        Returns
        -------
        numpy nd-array
        """
        if data is None:
            data = self.set_Mock_data()
        return data

    def grab_spectrum(self):
        return self.get_data_output()
