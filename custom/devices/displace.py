"""
Ideal Displace Device
"""

from quasi.devices import (
    GenericDevice,
    wait_input_compute,
    coordinate_gui,
    log_action,
    schedule_next_event,
    ensure_output_compute,
)
from quasi.devices.port import Port
from quasi.signals import GenericSignal, GenericFloatSignal, GenericQuantumSignal, GenericComplexSignal
from quasi.extra.logging import Loggers, get_custom_logger
from quasi.gui.icons import icon_list
from quasi.simulation import Simulation, SimulationType, ModeManager

from photon_weave.operation.fock_operation import FockOperationType, FockOperation

logger = get_custom_logger(Loggers.Devices)


class Displace(GenericDevice):
    """
    Implements Ideal Phase Shifter
    """

    ports = {
        "alpha": Port(
            label="alpha",
            direction="input",
            signal=None,
            signal_type=GenericComplexSignal,
            device=None,
        ),
        "input": Port(
            label="input",
            direction="input",
            signal=None,
            signal_type=GenericQuantumSignal,
            device=None,
        ),
        "output": Port(
            label="output",
            direction="output",
            signal=None,
            signal_type=GenericQuantumSignal,
            device=None,
        ),
    }

    gui_icon = icon_list.DISPLACE
    gui_tags = ["ideal"]
    gui_name = "Displacer"
    gui_documentation = "ideal_phase_shifter.md"

    power_peak = 0
    power_average = 0
    reference = None

    def __init__(self, name=None, time=0, uid=None):
        super().__init__(name=name, uid=uid)
        self.alpha = 0

    @ensure_output_compute
    @coordinate_gui
    @wait_input_compute
    def compute_outputs(self, *args, **kwargs):
        simulation = Simulation.get_instance()
        if simulation.simulation_type is SimulationType.FOCK:
            self.simulate_fock()

    @log_action
    @schedule_next_event
    def des(self, time=None, *args, **kwargs):
        if "alpha" in kwargs.get("signals"):
            self.alpha = kwargs["signals"]["alpha"].contents
        if "input" in kwargs.get("signals"):
            env = kwargs["signals"]["input"].contents
            fo = FockOperation(FockOperationType.Displace , alpha=self.alpha)
            env.apply_operation(fo)
            signal = GenericQuantumSignal()
            signal.set_contents(env)
            result = [("output", signal, time)]
            return result
