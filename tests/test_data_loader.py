"""Tests for DataLoader."""

from __future__ import annotations

import json
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from vectorlib import DataLoader


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

TELEMETRY_RECORDS: List[Dict[str, Any]] = [
    {"timestamp": "2024-01-01T00:00:00Z", "sensor": "A", "value": 10.0},
    {"timestamp": "2024-01-01T01:00:00Z", "sensor": "A", "value": 20.0},
    {"timestamp": "2024-01-01T02:00:00Z", "sensor": "B", "value": 15.0},
]

WEATHER_RECORDS: List[Dict[str, Any]] = [
    {"timestamp": "2024-01-01T00:00:00Z", "temperature": 5.0, "humidity": 80},
    {"timestamp": "2024-01-01T01:00:00Z", "temperature": 6.0, "humidity": 78},
    {"timestamp": "2024-01-01T02:00:00Z", "temperature": 7.0, "humidity": 75},
]


def _make_response(data: Any) -> MagicMock:
    """Return a mock requests.Response whose .json() returns *data*."""
    resp = MagicMock(spec=requests.Response)
    resp.json.return_value = data
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# from_records constructor
# ---------------------------------------------------------------------------

class TestFromRecords:
    def test_iter_yields_all_records(self):
        loader = DataLoader.from_records(TELEMETRY_RECORDS)
        result = list(loader)
        assert result == TELEMETRY_RECORDS

    def test_to_dataframe_shape(self):
        loader = DataLoader.from_records(TELEMETRY_RECORDS)
        df = loader.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (3, 3)

    def test_to_dataframe_empty_records(self):
        loader = DataLoader.from_records([])
        df = loader.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_merge_weather(self):
        loader = DataLoader.from_records(TELEMETRY_RECORDS, WEATHER_RECORDS, merge_on="timestamp")
        df = loader.to_dataframe()
        assert "temperature" in df.columns
        assert "humidity" in df.columns
        assert len(df) == 3

    def test_merge_weather_missing_key(self):
        """When merge_on key is absent, records are returned unmodified."""
        weather = [{"time": "2024-01-01T00:00:00Z", "temperature": 5.0}]
        loader = DataLoader.from_records(TELEMETRY_RECORDS, weather, merge_on="timestamp")
        df = loader.to_dataframe()
        # merge key not in weather → no weather columns added
        assert "temperature" not in df.columns

    def test_iter_can_be_called_multiple_times(self):
        loader = DataLoader.from_records(TELEMETRY_RECORDS)
        first = list(loader)
        second = list(loader)
        assert first == second


# ---------------------------------------------------------------------------
# HTTP-based constructor
# ---------------------------------------------------------------------------

class TestHTTPLoader:
    def test_fetch_list_response(self):
        session = MagicMock(spec=requests.Session)
        session.get.return_value = _make_response(TELEMETRY_RECORDS)

        loader = DataLoader(url="http://vector/api/records", session=session)
        result = list(loader)
        assert result == TELEMETRY_RECORDS
        session.get.assert_called_once_with(
            "http://vector/api/records", params={}, timeout=30
        )

    def test_fetch_dict_response_with_data_key(self):
        session = MagicMock(spec=requests.Session)
        session.get.return_value = _make_response({"data": TELEMETRY_RECORDS})

        loader = DataLoader(url="http://vector/api/records", session=session)
        result = list(loader)
        assert result == TELEMETRY_RECORDS

    def test_fetch_dict_response_with_records_key(self):
        session = MagicMock(spec=requests.Session)
        session.get.return_value = _make_response({"records": TELEMETRY_RECORDS})

        loader = DataLoader(url="http://vector/api/records", session=session)
        result = list(loader)
        assert result == TELEMETRY_RECORDS

    def test_fetch_unexpected_format_raises(self):
        session = MagicMock(spec=requests.Session)
        session.get.return_value = _make_response({"unknown_key": "value"})

        loader = DataLoader(url="http://vector/api/records", session=session)
        with pytest.raises(ValueError, match="Unexpected response format"):
            list(loader)

    def test_weather_merge_via_http(self):
        session = MagicMock(spec=requests.Session)

        def side_effect(url, **kwargs):
            if "weather" in url:
                return _make_response(WEATHER_RECORDS)
            return _make_response(TELEMETRY_RECORDS)

        session.get.side_effect = side_effect

        loader = DataLoader(
            url="http://vector/api/records",
            weather_url="http://weather/observations",
            session=session,
            merge_on="timestamp",
        )
        df = loader.to_dataframe()
        assert "temperature" in df.columns
        assert len(df) == 3

    def test_weather_url_none_skips_merge(self):
        session = MagicMock(spec=requests.Session)
        session.get.return_value = _make_response(TELEMETRY_RECORDS)

        loader = DataLoader(url="http://vector/api/records", session=session)
        df = loader.to_dataframe()
        assert "temperature" not in df.columns

    def test_custom_params_forwarded(self):
        session = MagicMock(spec=requests.Session)
        session.get.return_value = _make_response(TELEMETRY_RECORDS)

        loader = DataLoader(
            url="http://vector/api/records",
            params={"limit": 100},
            session=session,
        )
        list(loader)
        session.get.assert_called_once_with(
            "http://vector/api/records", params={"limit": 100}, timeout=30
        )

    def test_to_dataframe_returns_dataframe(self):
        session = MagicMock(spec=requests.Session)
        session.get.return_value = _make_response(TELEMETRY_RECORDS)

        loader = DataLoader(url="http://vector/api/records", session=session)
        df = loader.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["timestamp", "sensor", "value"]
