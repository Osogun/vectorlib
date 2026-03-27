"""Tests for DataCleaner."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from vectorlib import DataCleaner


# ---------------------------------------------------------------------------
# fill_missing
# ---------------------------------------------------------------------------

class TestFillMissing:
    @pytest.fixture()
    def series_with_nan(self) -> pd.Series:
        return pd.Series([1.0, np.nan, 3.0, np.nan, 5.0])

    def test_fill_mean(self, series_with_nan):
        result = DataCleaner.fill_missing(series_with_nan, method="mean")
        expected_fill = (1 + 3 + 5) / 3
        assert result.isna().sum() == 0
        assert result.iloc[1] == pytest.approx(expected_fill)

    def test_fill_median(self, series_with_nan):
        result = DataCleaner.fill_missing(series_with_nan, method="median")
        assert result.isna().sum() == 0
        assert result.iloc[1] == pytest.approx(3.0)

    def test_fill_mode(self):
        s = pd.Series([1.0, 1.0, np.nan, 2.0])
        result = DataCleaner.fill_missing(s, method="mode")
        assert result.isna().sum() == 0
        assert result.iloc[2] == 1.0

    def test_fill_ffill(self, series_with_nan):
        result = DataCleaner.fill_missing(series_with_nan, method="ffill")
        assert result.isna().sum() == 0
        assert result.iloc[1] == 1.0
        assert result.iloc[3] == 3.0

    def test_fill_bfill(self, series_with_nan):
        result = DataCleaner.fill_missing(series_with_nan, method="bfill")
        assert result.isna().sum() == 0
        assert result.iloc[1] == 3.0

    def test_fill_interpolate(self, series_with_nan):
        result = DataCleaner.fill_missing(series_with_nan, method="interpolate")
        assert result.isna().sum() == 0
        assert result.iloc[1] == pytest.approx(2.0)

    def test_fill_zero(self, series_with_nan):
        result = DataCleaner.fill_missing(series_with_nan, method="zero")
        assert result.iloc[1] == 0.0

    def test_unknown_method_raises(self, series_with_nan):
        with pytest.raises(ValueError, match="Unknown method"):
            DataCleaner.fill_missing(series_with_nan, method="bad_method")  # type: ignore

    def test_no_nan_unchanged(self):
        s = pd.Series([1.0, 2.0, 3.0])
        result = DataCleaner.fill_missing(s, method="mean")
        pd.testing.assert_series_equal(result, s)


# ---------------------------------------------------------------------------
# remove_outliers
# ---------------------------------------------------------------------------

class TestRemoveOutliers:
    @pytest.fixture()
    def series_with_outlier(self) -> pd.Series:
        return pd.Series([1.0, 2.0, 3.0, 4.0, 1000.0])

    def test_iqr_removes_outlier(self, series_with_outlier):
        result = DataCleaner.remove_outliers(series_with_outlier, method="iqr")
        assert np.isnan(result.iloc[4])
        assert result.iloc[0] == 1.0

    def test_zscore_removes_outlier(self):
        # Use a series where the outlier is clearly separated in z-score terms.
        s = pd.Series([2.0, 2.0, 3.0, 3.0, 100.0])
        result = DataCleaner.remove_outliers(s, method="zscore", threshold=1.5)
        assert np.isnan(result.iloc[4])

    def test_no_outliers_unchanged(self):
        s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = DataCleaner.remove_outliers(s, method="iqr")
        assert result.isna().sum() == 0

    def test_constant_series_zscore(self):
        s = pd.Series([5.0, 5.0, 5.0, 5.0])
        result = DataCleaner.remove_outliers(s, method="zscore")
        assert result.isna().sum() == 0

    def test_unknown_method_raises(self, series_with_outlier):
        with pytest.raises(ValueError, match="Unknown method"):
            DataCleaner.remove_outliers(series_with_outlier, method="bad")  # type: ignore


# ---------------------------------------------------------------------------
# normalize
# ---------------------------------------------------------------------------

class TestNormalize:
    @pytest.fixture()
    def series(self) -> pd.Series:
        return pd.Series([0.0, 5.0, 10.0])

    def test_minmax_range(self, series):
        result = DataCleaner.normalize(series, method="minmax")
        assert result.min() == pytest.approx(0.0)
        assert result.max() == pytest.approx(1.0)

    def test_zscore_mean_std(self):
        s = pd.Series([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
        result = DataCleaner.normalize(s, method="zscore")
        assert result.mean() == pytest.approx(0.0, abs=1e-10)
        assert result.std() == pytest.approx(1.0, abs=1e-10)

    def test_constant_series_minmax(self):
        s = pd.Series([3.0, 3.0, 3.0])
        result = DataCleaner.normalize(s, method="minmax")
        assert (result == 0.0).all()

    def test_constant_series_zscore(self):
        s = pd.Series([3.0, 3.0, 3.0])
        result = DataCleaner.normalize(s, method="zscore")
        assert (result == 0.0).all()

    def test_unknown_method_raises(self, series):
        with pytest.raises(ValueError, match="Unknown method"):
            DataCleaner.normalize(series, method="bad")  # type: ignore


# ---------------------------------------------------------------------------
# smooth
# ---------------------------------------------------------------------------

class TestSmooth:
    @pytest.fixture()
    def series(self) -> pd.Series:
        return pd.Series([1.0, 3.0, 5.0, 7.0, 9.0])

    def test_rolling_mean_values(self, series):
        result = DataCleaner.smooth(series, window=3, method="rolling_mean")
        assert len(result) == len(series)
        assert result.iloc[2] == pytest.approx(3.0)

    def test_ewm_values(self, series):
        result = DataCleaner.smooth(series, window=3, method="ewm")
        assert len(result) == len(series)
        # ewm should be between first and last value
        assert result.iloc[0] == pytest.approx(1.0)

    def test_unknown_method_raises(self, series):
        with pytest.raises(ValueError, match="Unknown method"):
            DataCleaner.smooth(series, method="bad")  # type: ignore


# ---------------------------------------------------------------------------
# remove_duplicates
# ---------------------------------------------------------------------------

class TestRemoveDuplicates:
    def test_dataframe_removes_duplicates(self):
        df = pd.DataFrame({"a": [1, 1, 2], "b": [10, 10, 20]})
        result = DataCleaner.remove_duplicates(df)
        assert len(result) == 2

    def test_series_removes_duplicates(self):
        s = pd.Series([1, 1, 2, 3, 3])
        result = DataCleaner.remove_duplicates(s)
        assert list(result) == [1, 2, 3]

    def test_keep_last(self):
        df = pd.DataFrame({"a": [1, 1, 2], "b": [10, 10, 20]})
        result = DataCleaner.remove_duplicates(df, keep="last")
        assert len(result) == 2


# ---------------------------------------------------------------------------
# drop_nulls
# ---------------------------------------------------------------------------

class TestDropNulls:
    def test_series_drops_nan(self):
        s = pd.Series([1.0, np.nan, 3.0])
        result = DataCleaner.drop_nulls(s)
        assert len(result) == 2

    def test_dataframe_drops_rows_with_any(self):
        df = pd.DataFrame({"a": [1.0, np.nan, 3.0], "b": [4.0, 5.0, 6.0]})
        result = DataCleaner.drop_nulls(df, how="any")
        assert len(result) == 2

    def test_dataframe_drops_rows_with_all(self):
        df = pd.DataFrame({"a": [1.0, np.nan, np.nan], "b": [4.0, np.nan, 6.0]})
        result = DataCleaner.drop_nulls(df, how="all")
        # Only the row where ALL values are NaN is dropped (row index 1)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# to_numeric / to_datetime
# ---------------------------------------------------------------------------

class TestTypeCoercions:
    def test_to_numeric_converts_strings(self):
        s = pd.Series(["1.0", "2.5", "abc"])
        result = DataCleaner.to_numeric(s, errors="coerce")
        assert result.iloc[0] == pytest.approx(1.0)
        assert np.isnan(result.iloc[2])

    def test_to_datetime_converts_strings(self):
        s = pd.Series(["2024-01-01", "2024-06-15"])
        result = DataCleaner.to_datetime(s)
        assert pd.api.types.is_datetime64_any_dtype(result)


# ---------------------------------------------------------------------------
# clip
# ---------------------------------------------------------------------------

class TestClip:
    def test_clip_lower(self):
        s = pd.Series([-5.0, 0.0, 5.0])
        result = DataCleaner.clip(s, lower=0.0)
        assert result.iloc[0] == 0.0

    def test_clip_upper(self):
        s = pd.Series([1.0, 5.0, 100.0])
        result = DataCleaner.clip(s, upper=10.0)
        assert result.iloc[2] == 10.0

    def test_clip_both(self):
        s = pd.Series([-1.0, 5.0, 20.0])
        result = DataCleaner.clip(s, lower=0.0, upper=10.0)
        assert result.iloc[0] == 0.0
        assert result.iloc[2] == 10.0
