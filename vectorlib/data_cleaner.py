"""
DataCleaner - static class with built-in tools for cleaning data series.
"""

from __future__ import annotations

from typing import Literal, Optional, Union

import numpy as np
import pandas as pd


class DataCleaner:
    """A collection of static utility methods for cleaning pandas data series
    and DataFrames.

    All methods are ``@staticmethod``\\ s so no instantiation is required::

        from vectorlib import DataCleaner

        clean = DataCleaner.fill_missing(series, method="mean")
    """

    # ------------------------------------------------------------------
    # Missing-value handling
    # ------------------------------------------------------------------

    @staticmethod
    def fill_missing(
        series: pd.Series,
        method: Literal["mean", "median", "mode", "ffill", "bfill", "interpolate", "zero"] = "mean",
    ) -> pd.Series:
        """Fill missing values in *series*.

        Parameters
        ----------
        series:
            Input data series.
        method:
            Strategy to use:

            * ``"mean"`` – replace NaN with the column mean.
            * ``"median"`` – replace NaN with the column median.
            * ``"mode"`` – replace NaN with the most frequent value.
            * ``"ffill"`` – forward-fill (propagate last valid observation).
            * ``"bfill"`` – backward-fill.
            * ``"interpolate"`` – linear interpolation.
            * ``"zero"`` – replace NaN with 0.

        Returns
        -------
        pandas.Series
            Series with missing values filled.
        """
        s = series.copy()
        if method == "mean":
            return s.fillna(s.mean())
        if method == "median":
            return s.fillna(s.median())
        if method == "mode":
            mode = s.mode()
            return s.fillna(mode.iloc[0] if not mode.empty else np.nan)
        if method == "ffill":
            return s.ffill()
        if method == "bfill":
            return s.bfill()
        if method == "interpolate":
            return s.interpolate()
        if method == "zero":
            return s.fillna(0)
        raise ValueError(
            f"Unknown method '{method}'. "
            "Choose from: mean, median, mode, ffill, bfill, interpolate, zero."
        )

    # ------------------------------------------------------------------
    # Outlier removal
    # ------------------------------------------------------------------

    @staticmethod
    def remove_outliers(
        series: pd.Series,
        method: Literal["iqr", "zscore"] = "iqr",
        threshold: float = 1.5,
    ) -> pd.Series:
        """Replace outliers with ``NaN``.

        Parameters
        ----------
        series:
            Numeric data series.
        method:
            Detection strategy:

            * ``"iqr"`` – values outside ``[Q1 - threshold*IQR, Q3 + threshold*IQR]``
              are considered outliers (default ``threshold=1.5``).
            * ``"zscore"`` – values whose absolute z-score exceeds *threshold*
              (default ``threshold=1.5`` for iqr; use e.g. ``3`` for zscore).

        threshold:
            Sensitivity of the chosen method.

        Returns
        -------
        pandas.Series
            Series with outliers replaced by ``NaN``.
        """
        s = series.copy().astype(float)
        if method == "iqr":
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - threshold * iqr, q3 + threshold * iqr
            return s.where((s >= lower) & (s <= upper))
        if method == "zscore":
            mean, std = s.mean(), s.std()
            if std == 0:
                return s
            z = (s - mean) / std
            return s.where(z.abs() <= threshold)
        raise ValueError(
            f"Unknown method '{method}'. Choose from: iqr, zscore."
        )

    # ------------------------------------------------------------------
    # Normalisation / scaling
    # ------------------------------------------------------------------

    @staticmethod
    def normalize(
        series: pd.Series,
        method: Literal["minmax", "zscore"] = "minmax",
    ) -> pd.Series:
        """Normalise a numeric series.

        Parameters
        ----------
        series:
            Numeric data series.
        method:
            Normalisation strategy:

            * ``"minmax"`` – scale to ``[0, 1]``.
            * ``"zscore"`` – standardise to zero mean and unit variance.

        Returns
        -------
        pandas.Series
        """
        s = series.copy().astype(float)
        if method == "minmax":
            mn, mx = s.min(), s.max()
            if mx == mn:
                return pd.Series(np.zeros(len(s)), index=s.index, name=s.name)
            return (s - mn) / (mx - mn)
        if method == "zscore":
            mean, std = s.mean(), s.std()
            if std == 0:
                return pd.Series(np.zeros(len(s)), index=s.index, name=s.name)
            return (s - mean) / std
        raise ValueError(
            f"Unknown method '{method}'. Choose from: minmax, zscore."
        )

    # ------------------------------------------------------------------
    # Smoothing
    # ------------------------------------------------------------------

    @staticmethod
    def smooth(
        series: pd.Series,
        window: int = 5,
        method: Literal["rolling_mean", "ewm"] = "rolling_mean",
    ) -> pd.Series:
        """Smooth a numeric series.

        Parameters
        ----------
        series:
            Numeric data series.
        window:
            Window size (for ``rolling_mean``) or span (for ``ewm``).
        method:
            Smoothing strategy:

            * ``"rolling_mean"`` – rolling (sliding window) mean.
            * ``"ewm"`` – exponentially weighted mean.

        Returns
        -------
        pandas.Series
        """
        s = series.copy().astype(float)
        if method == "rolling_mean":
            return s.rolling(window=window, min_periods=1).mean()
        if method == "ewm":
            return s.ewm(span=window, adjust=False).mean()
        raise ValueError(
            f"Unknown method '{method}'. Choose from: rolling_mean, ewm."
        )

    # ------------------------------------------------------------------
    # Duplicate handling
    # ------------------------------------------------------------------

    @staticmethod
    def remove_duplicates(
        data: Union[pd.DataFrame, pd.Series],
        subset: Optional[list] = None,
        keep: Literal["first", "last", False] = "first",
    ) -> Union[pd.DataFrame, pd.Series]:
        """Remove duplicate rows from a DataFrame (or duplicate values from a Series).

        Parameters
        ----------
        data:
            Input DataFrame or Series.
        subset:
            Column labels to consider for identifying duplicates (DataFrame only).
        keep:
            Which duplicate to keep: ``"first"``, ``"last"``, or ``False``
            (drop all duplicates).

        Returns
        -------
        pandas.DataFrame | pandas.Series
        """
        if isinstance(data, pd.Series):
            return data.drop_duplicates(keep=keep)
        return data.drop_duplicates(subset=subset, keep=keep)

    # ------------------------------------------------------------------
    # Null dropping
    # ------------------------------------------------------------------

    @staticmethod
    def drop_nulls(
        data: Union[pd.DataFrame, pd.Series],
        axis: int = 0,
        how: Literal["any", "all"] = "any",
    ) -> Union[pd.DataFrame, pd.Series]:
        """Drop rows (or columns) that contain null values.

        Parameters
        ----------
        data:
            Input DataFrame or Series.
        axis:
            ``0`` to drop rows, ``1`` to drop columns (DataFrame only).
        how:
            ``"any"`` – drop if *any* null is present; ``"all"`` – drop only if
            *all* values are null.

        Returns
        -------
        pandas.DataFrame | pandas.Series
        """
        if isinstance(data, pd.Series):
            return data.dropna()
        return data.dropna(axis=axis, how=how)

    # ------------------------------------------------------------------
    # Type coercion
    # ------------------------------------------------------------------

    @staticmethod
    def to_numeric(
        series: pd.Series,
        errors: Literal["raise", "coerce", "ignore"] = "coerce",
    ) -> pd.Series:
        """Convert *series* to a numeric dtype.

        Parameters
        ----------
        series:
            Input series.
        errors:
            How to handle values that cannot be converted (passed to
            :func:`pandas.to_numeric`).

        Returns
        -------
        pandas.Series
        """
        return pd.to_numeric(series, errors=errors)

    @staticmethod
    def to_datetime(
        series: pd.Series,
        fmt: Optional[str] = None,
        errors: Literal["raise", "coerce", "ignore"] = "coerce",
        utc: bool = False,
    ) -> pd.Series:
        """Convert *series* to datetime.

        Parameters
        ----------
        series:
            Input series containing date/time strings or timestamps.
        fmt:
            Optional strptime format string.
        errors:
            How to handle unparseable values.
        utc:
            Whether to return UTC-aware timestamps.

        Returns
        -------
        pandas.Series
        """
        return pd.to_datetime(series, format=fmt, errors=errors, utc=utc)

    # ------------------------------------------------------------------
    # Clipping
    # ------------------------------------------------------------------

    @staticmethod
    def clip(
        series: pd.Series,
        lower: Optional[float] = None,
        upper: Optional[float] = None,
    ) -> pd.Series:
        """Clip values in *series* to the interval ``[lower, upper]``.

        Parameters
        ----------
        series:
            Numeric series.
        lower:
            Minimum value (values below this are set to *lower*).
        upper:
            Maximum value (values above this are set to *upper*).

        Returns
        -------
        pandas.Series
        """
        return series.clip(lower=lower, upper=upper)
