import numpy as np


def _validate_interval(t1, t2, b1, b2):
    if t1 >= t2:
        raise ValueError(f"t1 must be < t2 (got t1={t1}, t2={t2}).")
    if b1 <= 0 or b2 <= 0:
        raise ValueError("Log-linear interpolation requires strictly positive b1 and b2.")


def interpolate(t, t1: float, t2: float, b1: float, b2: float):
    """Log-linear interpolation of a discount factor at time(s) t,
    between two known points (t1, b1) and (t2, b2).

    Linear interpolation on log(b) implies a piecewise-constant forward
    rate between t1 and t2, which is the standard convention for
    discount factor curves.

    Parameters
    ----------
    t : float or array_like
        Time(s) at which to interpolate. Can be a scalar or a vector;
        does not need to lie strictly within [t1, t2] (extrapolation
        is allowed but not validated).
    t1, t2 : float
        Known boundary times, t1 < t2.
    b1, b2 : float
        Known discount factors at t1 and t2 (must be strictly positive).

    Returns
    -------
    float or np.ndarray
        Interpolated discount factor(s), same shape as `t`.
    """
    _validate_interval(t1, t2, b1, b2)

    t = np.asarray(t, dtype=float)
    w2 = (t - t1) / (t2 - t1)
    w1 = 1.0 - w2

    result = np.exp(w1 * np.log(b1) + w2 * np.log(b2))

    return result.item() if result.ndim == 0 else result


def generate_subperiods(t1: float, t2: float, b1: float, b2: float,
                         n_periods: int, include_endpoints: bool = False):
    """Split [t1, t2] into n_periods equally-spaced sub-periods and
    log-linearly interpolate the discount factor at each internal point.

    Parameters
    ----------
    t1, t2 : float
        Boundary times of the period to split, t1 < t2.
    b1, b2 : float
        Known discount factors at t1 and t2.
    n_periods : int
        Number of sub-periods to create (>= 1). E.g. n_periods=4 splits
        [t1, t2] into 4 equal slices and returns the 3 internal break
        points (or 5 points total if include_endpoints=True).
    include_endpoints : bool
        If True, the returned times/values also include t1 and t2
        themselves (n_periods + 1 points in total). If False (default),
        only the internal break points are returned (n_periods - 1
        points).

    Returns
    -------
    times : np.ndarray
        Times of the generated points.
    values : np.ndarray
        Interpolated discount factors at those times.
    """
    if n_periods < 1:
        raise ValueError("n_periods must be >= 1.")

    if include_endpoints:
        times = np.linspace(t1, t2, n_periods + 1)
    else:
        times = np.linspace(t1, t2, n_periods + 1)[1:-1]

    values = np.atleast_1d(interpolate(times, t1, t2, b1, b2))

    return times, values


if __name__ == "__main__":
    t1, t2 = 1.0, 2.0
    b1, b2 = 0.9704, 0.9324

    times, values = generate_subperiods(t1, t2, b1, b2, n_periods=3)
    print("Punti interni (log-linear):")
    for tt, bb in zip(times, values):
        print(f"  t={tt:.3f} -> b={bb:.5f}")

    single_point = interpolate(1.5, t1, t2, b1, b2)
    print(f"\nInterpolazione puntuale a t=1.5: {single_point:.5f}")
