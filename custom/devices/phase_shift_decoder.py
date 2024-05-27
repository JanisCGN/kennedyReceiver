"""
Phase Shift Decoder
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
import time
import os
import math
import itertools

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
    GenericTimeSignal,
    GenericFloatSignal,
    GenericComplexSignal
)

from quasi.gui.icons import icon_list
from quasi.simulation import Simulation, SimulationType, ModeManager
from quasi.experiment import Experiment
from quasi.extra.logging import Loggers, get_custom_logger
from quasi.backend.envelope_backend import EnvelopeBackend
from photon_weave.state.envelope import Envelope
from photon_weave.state.composite_envelope import CompositeEnvelope
from photon_weave.operation.fock_operation import FockOperation, FockOperationType

logger = get_custom_logger(Loggers.Devices)


class PhaseShiftDecoder(GenericDevice):
    """
    Implements Ideal Single Photon Source
    """

    ports = {
        "frequency": Port(
            label="frequency",
            direction="input",
            signal=None,
            signal_type=GenericTimeSignal,
            device=None,
        ),
        "ps-1": Port(
            label="ps-1",
            direction="output",
            signal=None,
            signal_type=GenericComplexSignal,
            device=None,
        ),
        "ps-2": Port(
            label="ps-2",
            direction="output",
            signal=None,
            signal_type=GenericComplexSignal,
            device=None,
        ),
        "ps-3": Port(
            label="ps-3",
            direction="output",
            signal=None,
            signal_type=GenericComplexSignal,
            device=None,
        ),
    }

    # Gui Configuration
    gui_icon = icon_list.PHASE_SHIFT_DECODER
    gui_tags = ["ideal"]
    gui_name = "Displace Vals"
    gui_documentation = "switch.md"

    power_peak = 0
    power_average = 0
    reference = None

    def __init__(self, name=None, time=0, uid=None):
        super().__init__(name=name, uid=uid)
        self.frequency = None
        values = [-0.4, 0.4]
        self.phase_shifts = list(itertools.product(values, repeat=3))
        self.current_val = 0
        self.simulation = Simulation.get_instance()

    @ensure_output_compute
    @coordinate_gui
    @wait_input_compute
    def compute_outputs(self, *args, **kwargs):
        pass

    # des stands for discrete event simulation
    # decorators: schedule_next_event schedules the output to the next device. log_action logs that the component is computing
    @coordinate_gui
    @schedule_next_event
    @log_action
    def des(self, time, *args, **kwargs):
        print(time)
        if self.frequency is not None and self.current_val < len(self.phase_shifts): 
            results = []
            print("\nSCHEDULING EVENT PSD\n")
            for i,key in enumerate(["ps-1", "ps-2", "ps-3"]):
                signal = GenericComplexSignal()

                # Current value minus previous value
                pv = 0
                if not i == 0:
                    pv = self.phase_shifts[self.current_val][i-1]
                    
                ps = self.phase_shifts[self.current_val][i] - pv

                signal.set_complex(self.phase_shifts[self.current_val][i])
                results.append((key, signal, time))
                self.simulation.schedule_event(time + 1/self.frequency, self)

            self.current_val += 1
            return results

        if "frequency" in kwargs.get("signals"):
            self.frequency = kwargs["signals"]["frequency"].contents
            self.simulation.schedule_event(0, self)
