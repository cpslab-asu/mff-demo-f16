import dataclasses
import enum
import itertools
import math
import typing

import aerobench.examples.gcas.gcas_autopilot as gcas
import aerobench.run_f16_sim as f16
import numpy as np
import pandas as pd

TIME_STEPS: typing.Final[frozenset[float]] = frozenset({1/30, 1/40, 1/50, 1/60})


class Dynamics(enum.IntEnum):
    """Physics dynamics model.

    Stevens is a lookup-table method, Morelli uses differential equations. Morelli is higher-
    fidelity than Stevens.
    """

    STEVENS = 0
    MORELLI = 1

    def as_str(self) -> str:
        match self:
            case self.STEVENS:
                return "stevens"
            case self.MORELLI:
                return "morelli"


class Integrator(enum.IntEnum):
    """Solver integration method.

    Euler is a simple first-order integrator, RK45 is the Runge-Kutta 4(5) higher-order solver.
    RK45 is higher-fidelity than Euler.
    """

    EULER = 0
    RK45 = 1

    def as_str(self) -> str:
        match self:
            case self.EULER:
                return "euler"
            case self.RK45:
                return "rk45"


@dataclasses.dataclass()
class Configuration:
    """A simulation configuration.

    Args:
        time_step: The size of the time step to use for integration. Smaller is higher detail.
        dynamics: The dynamics model to use.
        integrator: The integration method to use

    Attributes:
        TMAX: Maximum simulation time
    """

    TMAX: typing.ClassVar[float] = 3.51

    time_step: float = dataclasses.field()
    dynamics: Dynamics = dataclasses.field()
    integrator: Integrator = dataclasses.field()

    def __lt__(self, other: object, /) -> bool:
        if not isinstance(other, Configuration):
            return NotImplemented

        return all([
            self.time_step > other.time_step,
            self.dynamics < other.dynamics,
            self.integrator < other.integrator,
        ])

    def simulate(self, alt: float = 1000, vt: float = 540) -> pd.DataFrame:
        """Run a F16 GCAS simulation with this configuration.

        Args:
            alt: The initial altitude of the aircraft
            vt: The initial velocity of aircraft

        Returns:
            A Pandas dataframe containing the aircraft state at each given integration step
        """

        ### Initial Conditions ###
        power = 9 # engine power level (0-10)

        # Default alpha & beta
        alpha = np.deg2rad(2.1215) # Trim Angle of Attack (rad)
        beta = 0                # Side slip angle (rad)

        # Initial Attitude
        phi = -math.pi/8           # Roll angle from wings level (rad)
        theta = (-math.pi/2)*0.3         # Pitch angle from nose level (rad)
        psi = 0   # Yaw angle from North (rad)

        # Build Initial Condition Vectors
        # state = [vt, alpha, beta, phi, theta, psi, P, Q, R, pn, pe, h, pow]
        init = [vt, alpha, beta, phi, theta, psi, 0, 0, 0, 0, 0, alt, power]
        ap = gcas.GcasAutopilot(init_mode='roll', stdout=True, gain_str='old')
        ap.llc.model_str = self.dynamics.as_str()
        res = f16.run_f16_sim(
            init,
            self.TMAX,
            ap,
            step=self.time_step,
            integrator_str=self.integrator.as_str(),
            extended_states=True,
        )
        states = res["states"]
        signals = np.array(res["u_list"], dtype=np.float64)

        return pd.DataFrame({
            "time": res["times"],
            "vel": states[:, 0],
            "alpha": states[:, 1],
            "beta": states[:, 2],
            "roll": states[:, 3],
            "pitch": states[:, 4],
            "yaw": states[:, 5],
            "roll_rate": states[:, 6],
            "pitch_rate": states[:, 7],
            "yaw_rate": states[:, 8],
            "north": states[:, 9],
            "east": states[:, 10],
            "altitude": states[:, 11],
            "thrust": states[:, 12],
            "modes": res["modes"],
            "throttle": signals[:, 0],
            "elevator": signals[:, 1],
            "aileron": signals[:, 2],
            "rudder": signals[:, 3],
        })


def configurations():
    """Set of all simulation configurations."""

    for tstep, backend, integrator in itertools.product(TIME_STEPS, Dynamics, Integrator):
        yield Configuration(tstep, backend, integrator)
