# Multi-Fidelity-Falsification F16 Example

## Getting Started

This project is build using [uv](https://docs.astral.sh/uv), which should be installed before starting.

With `uv` installed, you can setup the project environment using the following command:

```sh
uv sync
```

## Organization

The simulation configurations provided by this library can be found in the `simulation` module. Each
configuration has three options:

1. The timestep to use for the integrator
2. The model to use for the physics dynamics
3. The integration method to use for solving the dynamics equations

The set of all the simulation configurations can be obtained by using the `configurations()`
generator function. A simulation can be run by calling the `simulate` method on a `Configuration`
instance. This function returns a Pandas [`DataFrame`](https://https://pandas.pydata.org/docs/user_guide/dsintro.html#dataframe)
containing the states and controls for the aircraft for each timestep. The columns contained in the
`DataFrame` are the following:

| Column Name | Description                                       |
| ----------- | ------------------------------------------------- |
| time        | The time value for the associated values          |
| vel         | The airspeed of the aircraft in ft/s              |
| alpha       | The angle of attack of the aircraft in radians    |
| beta        | The side slip angle of the aircraft in radians    |
| roll        | The roll angle of the aircraft in radians         |
| pitch       | The pitch angle of the aircraft in radians        |
| yaw         | The yaw angle of the aircraft in radians          |
| roll_rate   | The rolling rate of the aircraft in rad/sec       |
| pitch_rate  | The pitching rate of the aircraft in rad/sec      |
| yaw_rate    | The yawing rate of the aircraft in rad/sec        |
| north       | The northward displacement of the aircraft in ft  |
| east        | The eastward displacement of the aircraft in ft   |
| altitude    | The height of the aircraft above the ground in ft |
| thrust      | The thrust of the aircraft (1 - 10)               |
| mode        | The mode of the aircraft (mode, standby, ...)     |
| throttle    | The throttle command to the aircraft (0.0, 1.0)   |
| elevator    | The elevator command to the aircraft in degrees   |
| aileron     | The aileron command to the aircraft in degrees    |
| rudder      | The rudder command to the aircraft in degrees     |

The `simulate` method accepts optional `alt` and `vt` arguments to set the initial altitude and
velocity.
