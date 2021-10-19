from PyQt5 import QtWidgets
from easydict import EasyDict as edict
from pymodaq.daq_utils.daq_utils import ThreadCommand, getLineInfo, DataFromPlugins, Axis
from pymodaq.daq_viewer.utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer

class DAQ_1DViewer_Spectro(DAQ_Viewer_base):
    """
    """
    params = comon_parameters+[
        {'title': 'Infos:', 'name': 'infos', 'type': 'str', 'value': ''},
        {'title': 'Amplitude:', 'name': 'amplitude', 'type': 'float', 'value': 1.},
        {'title': 'Width:', 'name': 'width', 'type': 'float', 'value': 10.},
        {'title': 'noise:', 'name': 'noise', 'type': 'float', 'value': 0.1},
        {'title': 'Grating::', 'name': 'grating', 'type': 'list', 'values': Spectrometer.gratings},

    ]

    def __init__(self, parent=None, params_state=None):
        super().__init__(parent, params_state)

        self.x_axis = None
        self.gratings_changed = False

    def commit_settings(self, param):
        """
        """
        ## TODO for your custom plugin
        if param.name() == "amplitude":
            self.controller.amplitude = param.value()
        elif param.name() == 'noise':
            self.controller.noise = param.value()
        elif param.name() == 'width':
            self.controller.width = param.value()
        elif param.name() == "grating":
            self.controller.grating = param.value()
            self.gratings_changed = True

        ##

    def get_xaxis(self):
        data_x_axis = self.controller.get_xaxis()  # if possible
        self.x_axis = Axis(data=data_x_axis, label='', units='')
        self.emit_x_axis()
        return self.x_axis

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object) custom object of a PyMoDAQ plugin (Slave case). None if only one detector by controller (Master case)

        Returns
        -------
        self.status (edict): with initialization status: three fields:
            * info (str)
            * controller (object) initialized controller
            *initialized: (bool): False if initialization failed otherwise True
        """

        try:
            self.status.update(edict(initialized=False,info="",x_axis=None,y_axis=None,controller=None))
            if self.settings.child(('controller_status')).value() == "Slave":
                if controller is None:
                    raise Exception('no controller has been defined externally while this detector is a slave one')
                else:
                    self.controller = controller
            else:
                ## TODO for your custom plugin
                self.controller = Spectrometer(wh=self.settings.child('width').value(),
                                               amp=self.settings.child('amplitude').value(),
                                               noise=self.settings.child('noise').value())  # any object that will control the stages
                #####################################
            self.settings.child('infos').setValue(self.controller.infos)
            ## TODO for your custom plugin
            # get the x_axis (you may want to to this also in the commit settings if x_axis may have changed
            #self.get_xaxis()

            ##############################

            self.status.info = self.controller.infos
            self.status.initialized = True
            self.status.controller = self.controller
            return self.status

        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status',[getLineInfo()+ str(e),'log']))
            self.status.info=getLineInfo()+ str(e)
            self.status.initialized=False
            return self.status

    def close(self):
        """
        Terminate the communication protocol
        """
        ## TODO for your custom plugin
        pass

    def grab_data(self, Naverage=1, **kwargs):
        """

        Parameters
        ----------
        Naverage: (int) Number of hardware averaging
        kwargs: (dict) of others optionals arguments
        """
        ## TODO for your custom plugin

        ##synchrone version (blocking function)


        data = self.controller.grab_spectrum()
        self.data_grabed_signal.emit([DataFromPlugins(name='MySpectro', data=[data],
                                                      dim='Data1D', labels=['Spectrum'],)])
        #########################################################
        if self.gratings_changed:
            self.get_xaxis()

        # ##asynchrone version (non-blocking function with callback)
        # self.controller.your_method_to_start_a_grab_snap(self.callback)
        # #########################################################



    def stop(self):

        pass

        return ''


if __name__ == '__main__':
    main(__file__)