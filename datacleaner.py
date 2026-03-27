import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer


class DataCleaner:

    @staticmethod
    def data_gaps(series):
        """
        Identify gaps (NaN sequences) in a pandas Series and number the positions within each gap.

        Parameters:
        series (pd.Series): Input pandas Series potentially containing NaN values.

        Returns:
        nan_values (pd.Series): A boolean Series indicating positions of NaN values (mask).
        gap_series (pd.Series): Series with the same index as input, where NaN positions contain the length of the NaN gap they belong to. Non-NaN positions are NaN.
        gap_groups (pd.core.groupby.generic.SeriesGroupBy): A groupby object grouping NaN positions by their gap.
        """

        nan_values = series.isna()
        gaps = (nan_values != nan_values.shift()).cumsum()
        gap_groups = nan_values[nan_values].groupby(gaps[nan_values])
        gap_series = pd.Series(dtype=int, index=series.index)
        for group_label, s in gap_groups:
            gap_series[s.index] = len(s)
        return nan_values, gap_series, gap_groups

    @staticmethod
    def fill_nan_values(df, col, method, max_gap=None, time_window=5, n_neighbors=5):
        """
        Fill NaN values in a pandas Series using specified method.

        Parameters:
        df (pd.DataFrame): Input DataFrame containing the column to fill.
        col (str): Name of the column in df to fill NaN values in.
        method (str): Method to use for filling NaN values. Options:
            - 'interpolate' : Use linear interpolation to fill NaN values. If the index is a DatetimeIndex, time-based interpolation is used.
            - 'mean': Fill NaN values with rolling mean over specified time window.
            - 'knn': Use KNN imputation based on other numerical features in the DataFrame.
        max_gap (int): Maximum number of consecutive NaN values to fill. If None, no limit is applied.
        time_window (int): Window size for rolling mean if method='mean'. Default is 5.
        n_neighbors (int): Number of neighbors to use for KNN imputation if method='knn'. Default is 5.


        """

        df = df.copy()
        if method == "interpolate":
            # check if timeseries or series
            if isinstance(df.index, pd.DatetimeIndex):
                # if max_gap>len(df) interpolation will fail, so we set max_gap to len(df)-1
                max_gap = min(max_gap, len(df) - 1) if max_gap is not None else None
                s = df[col].interpolate(
                    method="time", limit=max_gap, limit_area="inside"
                )
            else:
                s = df[col].interpolate(
                    method="linear", limit=max_gap, limit_area="inside"
                )
            if max_gap is not None:
                s = s.ffill(limit=max_gap)
                s = s.bfill(limit=max_gap)
            df[col] = s
        elif method == "mean":
            rolling = (
                df[col].rolling(window=time_window, min_periods=1, center=True).mean()
            )
            df[col] = df[col].fillna(rolling)
        elif method == "knn":
            features = df.select_dtypes("number").dropna(axis=1, how="all")
            imputer = KNNImputer(n_neighbors=n_neighbors)
            imputed_df = imputer.fit_transform(features)
            df[col] = imputed_df[:, features.columns.get_loc(col)]
        else:
            raise ValueError("Unknown method for filling NaN values.")

        return df[col]

    @staticmethod
    def remove_outliers(
        series,
        method="iqr",
        k=1.5,
        q_low=0.05,
        q_high=0.95,
        winsorization=True,
        rolling=False,
        time_window=24,
    ):
        """
        Detect and replace outliers in a pandas Series with NaN values.

        Parameters:
        series (pd.Series): Input pandas Series with numerical values.
        method (str): Method for outlier detection. Options:
            - '3sigma': Three-sigma rule (values beyond 3 standard deviations from mean)
            - 'MAD': Median Absolute Deviation method (values beyond 3*MAD from median)
            - 'iqr': Interquartile Range method (default)
            - 'quantile': Quantile-based method (values outside specified quantiles)
        k (float): Multiplier for IQR method (default is 1.5).
                Lower values are more aggressive, higher values are more conservative.
        q_low (float): Lower quantile for 'quantile' method (default is 0.05).
        q_high (float): Upper quantile for 'quantile' method (default is 0.95).
        winsorization (bool): If True, replace outliers with boundary values instead of NaN. Default is True.
        rolling (bool): If True, use rolling statistics for outlier detection. Default is False.
        time_window (int): Window size for rolling statistics if rolling=True. Default is 24

        Returns:
        pd.Series: Series with outliers replaced by NaN or boundary values if winsorization is True.

        Note:
        - '3sigma': Assumes normal distribution. Outliers are |value - mean| > 3*std
        - 'MAD': More robust to non-normal distributions. Outliers are |value - median| > 3*MAD
        - 'iqr': More robust to extreme values. Outliers are outside [Q1 - k*IQR, Q3 + k*IQR]
        - 'quantile': Outliers are outside [Q_low, Q_high] quantiles.
        - using 'rolling' makes computation longer but adapts to local data patterns. 'rolling' with 'quantile' may be very slow for large datasets.
        """
        series = series.copy()
        if method == "3sigma":
            if rolling:
                mean = series.rolling(window=time_window, min_periods=1).mean()
                std = series.rolling(window=time_window, min_periods=1).std()
            else:
                mean = series.mean()
                std = series.std()
            threshold = 3 * std
            outliers = (series - mean).abs() > threshold
            if winsorization:
                series[outliers & (series > mean)] = mean + threshold
                series[outliers & (series < mean)] = mean - threshold
            else:
                series[outliers] = np.nan
        elif method == "MAD":
            if rolling:
                median = series.rolling(window=time_window, min_periods=1).median()
                mad = (
                    (series - median)
                    .abs()
                    .rolling(window=time_window, min_periods=1)
                    .median()
                )
            else:
                median = series.median()
                mad = (series - median).abs().median()
            threshold = 3 * 1.4826 * mad
            outliers = (series - median).abs() > threshold
            if winsorization:
                series[outliers & (series > median)] = median + threshold
                series[outliers & (series < median)] = median - threshold
            else:
                series[outliers] = np.nan
        elif method == "iqr":
            if rolling:
                Q1 = series.rolling(window=time_window, min_periods=1).quantile(0.25)
                Q3 = series.rolling(window=time_window, min_periods=1).quantile(0.75)
            else:
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - k * IQR
            upper_bound = Q3 + k * IQR
            outliers = (series < lower_bound) | (series > upper_bound)
            if winsorization:
                series[outliers & (series > upper_bound)] = upper_bound
                series[outliers & (series < lower_bound)] = lower_bound
            else:
                series[outliers] = np.nan
        elif method == "quantile":
            if rolling:
                Q_low = series.rolling(window=time_window, min_periods=1).quantile(
                    q_low
                )
                Q_high = series.rolling(window=time_window, min_periods=1).quantile(
                    q_high
                )
            else:
                Q_low = series.quantile(q_low)
                Q_high = series.quantile(q_high)
            outliers = (series < Q_low) | (series > Q_high)
            if winsorization:
                series[outliers & (series > Q_high)] = Q_high
                series[outliers & (series < Q_low)] = Q_low
            else:
                series[outliers] = np.nan
        else:
            raise ValueError(
                "Unsupported method. Use '3sigma', 'MAD', 'iqr', or 'quantile'."
            )

        return series

    @staticmethod
    def fill_nan_values_old(series, max_gap, method="linear"):
        """
        Fill NaN values in a pandas Series based on neighboring values, but only for gaps shorter than max_gap.

        The function identifies each gap (sequence of NaN values) and fills it using values from a time window
        around the gap. The time window is determined by the dominant time interval in the series index.

        Parameters:
        series (pd.Series): Input pandas Series with DatetimeIndex potentially containing NaN values.
        max_gap (int): Maximum length of NaN gaps to fill. Longer gaps are left as NaN.
        method (str): Method for filling NaN values. Options:
            - 'linear': Linear interpolation between values before and after the gap
            - 'mean': Mean of values in the time window around the gap
            Default is 'linear'.

        Returns:
        series (pd.Series): Series with NaN values filled where gaps are shorter than max_gap. Modifies series in place.
        Note:
        Gaps equal to or longer than max_gap are skipped.
        """
        series = series.copy()
        nan_mask, gap_series, gap_groups = DataCleaner.data_gaps(series)

        freq = pd.infer_freq(series.index)
        if freq is None:
            raise ValueError("Cannot infer time frequency of index.")
        timedelta_value = pd.to_timedelta("1" + freq)

        for gaplabel, s in gap_groups:
            if len(s) > max_gap:
                continue
            nan_indexes = s.index
            timebefore = nan_indexes[0] - timedelta_value
            timeafter = nan_indexes[-1] + timedelta_value

            # Określenie okna czasowego do uzupełniania
            timebefore_in_index = timebefore in series.index
            timeafter_in_index = timeafter in series.index

            if timebefore_in_index and not timeafter_in_index:
                combined_index = pd.DatetimeIndex([timebefore] + list(nan_indexes))
                series_subset = series.loc[combined_index]
                series.loc[nan_indexes] = series_subset.ffill().loc[nan_indexes]
            elif not timebefore_in_index and timeafter_in_index:
                combined_index = pd.DatetimeIndex(list(nan_indexes) + [timeafter])
                series_subset = series.loc[combined_index]
                series.loc[nan_indexes] = series_subset.bfill().loc[nan_indexes]
            elif timebefore_in_index and timeafter_in_index:
                combined_index = pd.DatetimeIndex(
                    [timebefore] + list(nan_indexes) + [timeafter]
                )
                series_subset = series.loc[combined_index]
                if method == "linear":
                    series.loc[nan_indexes] = series_subset.interpolate(
                        method="linear"
                    ).loc[nan_indexes]
                elif method == "mean":
                    mean_value = series_subset.dropna().mean()
                    series.loc[nan_indexes] = mean_value
                else:
                    raise ValueError("Unsupported filling NaN values method.")
            # If neither timebefore nor timeafter is in index, skip this gap
            # as we don't have enough data to fill it

        return series
