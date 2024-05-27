"""
Wigner Plot
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
import time
import os

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


class WignerPlot(GenericDevice):
    """
    Implements Ideal Single Photon Source
    """

    ports = {
        "input-1": Port(
            label="input-1",
            direction="input",
            signal=None,
            signal_type=GenericQuantumSignal,
            device=None,
        ),
        "input-2": Port(
            label="input-2",
            direction="input",
            signal=None,
            signal_type=GenericQuantumSignal,
            device=None,
        ),
        "input-3": Port(
            label="input-3",
            direction="input",
            signal=None,
            signal_type=GenericQuantumSignal,
            device=None,
        ),
        "end": Port(
            label="end",
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
        "output-3": Port(
            label="output-3",
            direction="output",
            signal=None,
            signal_type=GenericQuantumSignal,
            device=None,
        ),
    }

    # Gui Configuration
    gui_icon = icon_list.WIGNER_CONTROL
    gui_tags = ["ideal"]
    gui_name = "Custim Wigner"
    gui_documentation = "switch.md"

    power_peak = 0
    power_average = 0
    reference = None

    def __init__(self, name=None, time=0, uid=None):
        super().__init__(name=name, uid=uid)
        self.rounds = 0
        self.should_output = True

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
        print("WIGNER")
        #######################
        # Catching the inputs #
        #######################
        if "end" in kwargs.get("signals"):
            print("END")
            self.should_output = kwargs["signals"]["end"].contents

        keys = ["input-1", "input-2", "input-3"]
        keys_set = set(keys)
        intersecting_keys = keys_set.intersection(kwargs.get("signals"))
        results = []
        for key in intersecting_keys:
            print(f"\n PRINTING WIGNER {key} \n")
            env = kwargs["signals"][key].contents
            state = env.fock.get_subspace()

            # Generate the wigner plot
            qobj = qt.Qobj(state)
            x = np.linspace(-5, 5, 100)
            p = np.linspace(-5, 5, 100)
            W = qt.wigner(qobj, x, p)
            X, P = np.meshgrid(x, p)
            plt.contourf(X, P, W, 100, cmap="RdBu")
            plt.colorbar()
            plt.xlabel("Position x")
            plt.ylabel("Momentum p")
            plt.title("Wigner Function")
            script_dir = os.path.dirname(__file__)
            plot_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "plots"))
            filename = f"wp-{key}-{time}.png"
            filepath = os.path.join(
                plot_dir, filename
            )  # Creates full path to store the file

            plt.savefig(filepath)
            plt.close()

            signal = kwargs["signals"][key]
            key = key.replace("input", "output")
            results.append((key, signal, time))

        if self.should_output:
            return results
