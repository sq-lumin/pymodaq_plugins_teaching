from pymodaq.daq_move.utility_classes import DAQ_Move_base  # base class
from pymodaq.daq_move.utility_classes import comon_parameters_fun, main  # common set of parameters for all actuators
from pymodaq.daq_utils.daq_utils import ThreadCommand  # object used to send info back to the main thread

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer


class DAQ_Move_Monochromator(DAQ_Move_base):
    """Plugin for the Template Instrument

    This object inherits all functionality to communicate with PyMoDAQ Module through inheritance via DAQ_Move_base
    It then implements the particular communication with the instrument

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library
    # TODO add your particular attributes here if any

    """
    _controller_units = 'whatever'  # TODO for your plugin: put the correct unit here
    is_multiaxes = True  # TODO for your plugin set to True if this plugin is controlled for a multiaxis controller
    axes_names = ['Axis1', 'Axis2']  # TODO for your plugin: complete the list

    params = [   # TODO for your custom plugin: elements to be added here as dicts in order to control your custom stage
                ] + comon_parameters_fun(is_multiaxes, axes_names)

    def ini_attributes(self):
        #TODO declare here attributes you want/need to init with a default value
        self.controller: Spectrometer = None

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        pos = self.controller.get_wavelength()  # when writing your own plugin replace this line
        pos = self.get_position_with_scaling(pos)
        return pos

    def close(self):
        """Terminate the communication protocol"""
        self.controller.close_communication()

    def commit_settings(self, param):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        if param.name() == "a_parameter_you've_added_in_self.params":
           self.controller.your_method_to_apply_this_param_change()
        else:
            pass

    def ini_stage(self, controller: Spectrometer = None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.ini_stage_init(old_controller=controller,
                            new_controller=Spectrometer())
        info = "Whatever info you want to log"
        initialized = self.controller.open_communication()  # or False if your hardware coun't be initialized
        return info, initialized

    def move_abs(self, value):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """

        value = self.check_bound(value)  #if user checked bounds, the defined bounds are applied here
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one

        self.controller.set_wavelength(value)  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        self.target_position = value

    def move_rel(self, value):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_position = value + self.current_position
        self.controller.set_wavelength(value, set_type='rel')  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))


    def move_home(self):
        """Call the reference method of the controller"""

        self.move_abs(532)
        self.poll_moving()


    def stop_motion(self):
      """Stop the actuator and emits move_done signal"""
      self.controller.stop()  # when writing your own plugin replace this line
      self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))


if __name__ == '__main__':
    main(__file__)
