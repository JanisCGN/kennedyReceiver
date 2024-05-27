"""
Ideal Single Photon Source implementation
"""

import numpy as np

from quasi.devices import (
    GenericDevice,
    wait_input_compute,
    coordinate_gui,
    schedule_next_event,
    log_action,
    ensure_output_compute,
)
from quasi.devices.port import Port
from quasi.signals import (
    GenericSignal,
    GenericBoolSignal,
    GenericIntSignal,
    GenericQuantumSignal,
)

from quasi.gui.icons import icon_list
from quasi.simulation import Simulation, SimulationType, ModeManager
from quasi.experiment import Experiment
from quasi.extra.logging import Loggers, get_custom_logger
from quasi.backend.envelope_backend import EnvelopeBackend
from photon_weave.state.envelope import Envelope
from photon_weave.operation.fock_operation import FockOperation, FockOperationType

logger = get_custom_logger(Loggers.Devices)


class Switch(GenericDevice):
    """
    Implements Ideal Single Photon Source
    """

    ports = {
        "input": Port(
            label="input",
            direction="input",
            signal=None,
            signal_type=GenericSignal,
            device=None,
        ),
        "switch": Port(
            label="switch",
            direction="input",
            signal=None,
            signal_type=GenericBoolSignal,
            device=None,
        ),
        "output-1": Port(
            label="output-1",
            direction="output",
            signal=None,
            signal_type=GenericQuantumSignal,
            device=None,
        ),
        "output-2": Port(
            label="output-2",
            direction="output",
            signal=None,
            signal_type=GenericQuantumSignal,
            device=None,
        ),
    }

    # Gui Configuration
    gui_icon = icon_list.SWITCH
    gui_tags = ["ideal"]
    gui_name = "Switch"
    gui_documentation = "switch.md"

    power_peak = 0
    power_average = 0
    reference = None

    def __init__(self, name=None, time=0, uid=None):
        super().__init__(name=name, uid=uid)
        self.active_output_port = "output-1"

    @ensure_output_compute
    @coordinate_gui
    @wait_input_compute
    def compute_outputs(self, *args, **kwargs):
        """
        Compute outputs for fock simulation
        """

    @coordinate_gui
    @schedule_next_event
    @log_action
    def des(self, time, *args, **kwargs):
        if "switch" in kwargs.get("signals"):
            if kwargs["signals"]["switch"].contents:
                self.active_output_port = "output-2"
            else:
                self.active_output_port = "output-1"
        if "input" in kwargs.get("signals"):
            signal = kwargs["signals"]["input"]
            results = [(self.active_output_port, signal, time)]
            return results
