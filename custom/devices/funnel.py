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


class Funnel(GenericDevice):
    """
    Implements Ideal Single Photon Source
    """

    ports = {
        "input-1": Port(
            label="input-1",
            direction="input",
            signal=None,
            signal_type=GenericSignal,
            device=None,
        ),
        "input-2": Port(
            label="input-2",
            direction="input",
            signal=None,
            signal_type=GenericSignal,
            device=None,
        ),
        "input-3": Port(
            label="input-3",
            direction="input",
            signal=None,
            signal_type=GenericSignal,
            device=None,
        ),
        "output": Port(
            label="output",
            direction="output",
            signal=None,
            signal_type=GenericSignal,
            device=None,
        ),
    }

    # Gui Configuration
    gui_icon = icon_list.FUNNEL
    gui_tags = ["ideal"]
    gui_name = "Funnel"
    gui_documentation = "memory.md"

    power_peak = 0
    power_average = 0
    reference = None

    def __init__(self, name=None, time=0, uid=None):
        super().__init__(name=name, uid=uid)
        self.photon_num = None

    def set_photon_num(self, photon_num: int):
        """
        Set the number of photons the source should emit in a pulse
        """
        photon_num_sig = GenericIntSignal()
        photon_num_sig.set_int(photon_num)
        self.register_signal(signal=photon_num_sig, port_label="photon_num")
        photon_num_sig.set_computed()

    @ensure_output_compute
    @coordinate_gui
    @wait_input_compute
    def compute_outputs(self, *args, **kwargs):
        pass

    @coordinate_gui
    @schedule_next_event
    @log_action
    def des(self, time, *args, **kwargs):
        if any(
            key in kwargs.get("signals") for key in ["input-1", "input-2", "input-3"]
        ):
            for key in kwargs["signals"]:
                sig = kwargs["signals"][key]
                return [("output", sig, time)]
