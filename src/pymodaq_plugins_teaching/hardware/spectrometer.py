import numpy as np
from pymodaq.daq_utils.daq_utils import gauss1D

class Spectrometer:

    axis = ['lambda0']
    gratings = ['G300', 'G1200']

    Nactuators = len(axis)
    Nx = 256
    infos = 'Spectrometer Controller Wrapper 0.0.1'

    def __init__(self, positions=[632.], noise=0.1, amp=10, wh=20, grating=gratings[0]):
        super().__init__()
        if positions is None:
            self.current_positions = dict(zip(self.axis, [0. for ind in range(self.Nactuators)]))
        else:
            assert isinstance(positions, list)
            assert len(positions) == self.Nactuators
            self.current_positions = dict(zip(self.axis, positions))

        self._amp = amp
        self._noise = noise
        self._wh = wh
        self._grating = grating

    @property
    def grating(self):
        return self._grating

    @grating.setter
    def grating(self, grat):
        if grat in self.gratings:
            self._grating = grat

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

    def set_wavelength(self, value, set_type='abs'):
        if value < 0:
            raise ValueError('Wavelength cannot be negative')

        if set_type == 'abs':
            self.current_positions['lambda0'] = value
        else:
            self.current_positions['lambda0'] += value

    def get_wavelength(self):
        return self.current_positions['lambda0']

    def get_xaxis(self):
        if self._grating == 'G300':
            coeff = 0.7
        elif self._grating == 'G1200':
            coeff = 0.25
        return (np.linspace(0, self.Nx, self.Nx, endpoint=False) - self.Nx / 2) * coeff +\
               self.current_positions['lambda0']

    def set_Mock_data(self):
        """
        """
        x_axis = self.get_xaxis()
        return self._amp * gauss1D(x_axis, self.current_positions['lambda0'], self._wh) +\
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
