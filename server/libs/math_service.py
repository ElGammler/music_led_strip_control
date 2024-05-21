from functools import wraps

import numpy as np


class MathService:
    @staticmethod
    def interpolate(y, new_length) -> np.array:
        """Intelligently resizes the array by linearly interpolating the values.

        Parameters
        ----------
        y : np.array
            Array that should be resized

        new_length : int
            The length of the new interpolated array

        Returns
        -------
        z : np.array
            New array with length of new_length that contains the interpolated
            values of y.

        """
        if len(y) == new_length:
            return y
        x_old = _normalized_linspace(len(y))
        x_new = _normalized_linspace(new_length)
        return np.interp(x_new, x_old, y)


def memoize(function):
    """Provide a decorator for memoizing functions."""
    memo = {}

    @wraps(function)
    def wrapper(*args):
        if args in memo:
            return memo[args]
        rv = function(*args)
        memo[args] = rv
        return rv
    return wrapper


@memoize
def _normalized_linspace(size):
    return np.linspace(0, 1, size)
