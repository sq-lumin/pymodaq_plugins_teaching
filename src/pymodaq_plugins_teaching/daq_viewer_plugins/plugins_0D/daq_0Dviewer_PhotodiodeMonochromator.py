import numpy as np
from qtpy.QtCore import QObject, Slot, Signal, QThread
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer


# TODO:
# (1) change the name of the following class to DAQ_0DViewer_TheNameOfYourChoice
# (2) change the name of this file to daq_0Dviewer_TheNameOfYourChoice ("TheNameOfYourChoice" should be the SAME
#     for the class name and the file name.)
# (3) this file should then be put into the right folder, namely IN THE FOLDER OF THE PLUGIN YOU ARE DEVELOPING:
#     pymodaq_plugins_my_plugin/daq_viewer_plugins/plugins_0D
class DAQ_0DViewer_PhotodiodeMonochromator(DAQ_Viewer_base):
    """ Instrument plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of instruments that should be compatible with this instrument plugin.
        * With which instrument it has actually been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
    """
    params = comon_parameters+[
        ## TODO for your custom plugin: elements to be added here as dicts in order to control your custom stage
        ]

    callback_signal = Signal()

    def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
        self.controller: Spectrometer = None

        #TODO declare here attributes you want/need to init with a default value
        pass

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        if param.name() == "a_parameter_you've_added_in_self.params":
           self.controller.your_method_to_apply_this_param_change()  # when writing your own plugin replace this line
#        elif ...
        ##

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.ini_detector_init(old_controller=controller,
                               new_controller=Spectrometer())

        self.dte_signal_temp.emit(DataToExport(name='photodiode_monochromator',
                                               data=[DataFromPlugins(name='intensity',
                                                                     data=[np.array([0])],
                                                                     dim='Data0D',
                                                                     labels=['Intensity'])]))
        # init stuff for async operation
        callback = MyCallback(self.controller.wait_photodiode_monochromator)
        self.callback_thread = QThread()
        callback.moveToThread(self.callback_thread)
        callback.data_sig.connect(self.callback)

        self.callback_signal.connect(callback.wait_for_acquisition)
        self.callback_thread.callback = callback
        self.callback_thread.start()

        info = "Monochromator OD Viewer Initialized"
        initialized = self.controller.open_communication()
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        self.controller.close_communication()

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        ## TODO for your custom plugin: you should choose EITHER the synchrone or the asynchrone version following

        # synchrone version (blocking function)
        #data_tot = self.controller.grab_monochromator()
        #self.dte_signal.emit(DataToExport(name='photodiode_monochromator',
        #                                  data=[DataFromPlugins(name='intensity', data=data_tot,
        #                                                        dim='Data0D', labels=['Intensity'])]))
        #########################################################

        # asynchrone version (non-blocking function with callback)
        self.callback_signal.emit()
        # self.controller.your_method_to_start_a_grab_snap(self.callback)  # when writing your own plugin replace this line
        #########################################################

    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.get_async_data_0D()
        self.dte_signal.emit(DataToExport(name='photodiode_monochromator',
                                          data=[DataFromPlugins(name='intensity', data=data_tot,
                                                                dim='Data0D', labels=['Intensity'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        raise NotImplementedError
        # self.controller.stop()  # this is only for moving
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        ##############################
        return ''


class MyCallback(QObject):

    data_sig = Signal()
    def __init__(self,wait_fn):
        super().__init__()
        self.wait_fn = wait_fn

    def wait_for_acquisition(self):
        err = self.wait_fn()

        if err != -1:
            self.data_sig.emit()


if __name__ == '__main__':
    main(__file__)
