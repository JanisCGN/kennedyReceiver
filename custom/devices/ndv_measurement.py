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


class NdvMeasurement(GenericDevice):
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
        "output-frequency": Port(
            label="output-frequency",
            direction="input",
            signal=None,
            signal_type=GenericTimeSignal,
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
        "measurement-result": Port(
            label="measurement-result",
            direction="output",
            signal=None,
            signal_type=GenericBoolSignal,
            device=None,
        ),
    }

    # Gui Configuration
    gui_icon = icon_list.NON_DESTRUCTIVE_MEASUREMENT
    gui_tags = ["ideal"]
    gui_name = "NDV Measurement"
    gui_documentation = "switch.md"

    power_peak = 0
    power_average = 0
    reference = None

    def __init__(self, name=None, time=0, uid=None):
        super().__init__(name=name, uid=uid)
        # here is our expected input
        self.register = {"input-1": None, "input-2": None, "input-3": None}
        # How long does it take to process inputs
        self.processing_time = 0.00001
        # Default output frequency
        #  - frequency at which the outputs are produced after failed measurement
        self.output_frequency = 100

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
        #######################
        # Catching the inputs #
        #######################
        if "output-frequency" in kwargs.get("signals"):
            self.output_frequency = kwargs["signals"]["output-frequency"].contents
        if "input-1" in kwargs.get("signals"):
            self.register["input-1"] = kwargs["signals"]["input-1"].contents
        if "input-2" in kwargs.get("signals"):
            self.register["input-2"] = kwargs["signals"]["input-2"].contents
        if "input-3" in kwargs.get("signals"):
            self.register["input-3"] = kwargs["signals"]["input-3"].contents

        # If all registers contain a pulse, we perform non destructive joint
        # measurement
        if (
            self.register["input-1"]
            and self.register["input-2"]
            and self.register["input-3"]
        ):
            envelopes = [
                self.register["input-1"],
                self.register["input-2"],
                self.register["input-3"],
            ]
            # Generating Composite Envelope
            ce = CompositeEnvelope(*envelopes)

            # Combining fock spaces, if not yet combined
            ce.combine(*[env.fock for env in envelopes])

            #############
            # Measuring #
            #############

            # Generating the two operators
            P_vac = vacuum_measurement_operator(*envelopes)
            P_oth = non_vacuum_measurement_operator(*envelopes)
            # Measuring
            outcome = ce.POVM_measurement(
                [env.fock for env in envelopes], [P_vac, P_oth]
            )
            results = []
            # Integer outcome correspond to the index of the measurement operator
            if outcome == 0:
                # Output the outcome signal on the measurement-result port
                sig = GenericBoolSignal()
                sig.set_bool(True)
                results.append(("measurement-result", sig, time + self.processing_time))
                print("measured vacuum, horay!")
            if outcome == 1:
                # Output the pulses on the corresponding ports in the correct intervals
                time = time + self.processing_time
                for key in self.register:
                    sig = GenericQuantumSignal()
                    # Set the contents of the signal
                    sig.set_contents(self.register[key])
                    key = key.replace("input", "output")
                    results.append((key, sig, time))
                    time += 1 / self.output_frequency

            # Clear the registers after measuring
            self.register["input-1"] = None
            self.register["input-2"] = None
            self.register["input-3"] = None

            return results


def vacuum_measurement_operator(*envelopes):
    P = 1
    for envelope in envelopes:
        # We generate vacuum state for all envelopes we try to measure
        vacuum = np.zeros((envelope.fock.dimensions, envelope.fock.dimensions))
        vacuum[0][0] = 1
        # Vacuum state is then included in the tensor product
        P = np.kron(P, vacuum)
    return P


def non_vacuum_measurement_operator(*envelopes):
    P = 1
    for envelope in envelopes:
        P = np.kron(P, np.eye(envelope.fock.dimensions))

    P = P - vacuum_measurement_operator(*envelopes)
    return P
