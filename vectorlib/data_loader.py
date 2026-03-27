"""
DataLoader - generator for fetching data from Vector / Vector clone,
merging with weather data, and exporting to a pandas DataFrame.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Generator, Iterable, Iterator, List, Optional

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class DataLoader:
    """Generator-based loader for telemetry data from a Vector (or Vector-compatible)
    source. Optionally merges records with weather data and can export the result
    to a :class:`pandas.DataFrame`.

    Parameters
    ----------
    url:
        Base URL of the Vector / Vector-clone HTTP endpoint.
    weather_url:
        Optional URL of a weather API endpoint.  When supplied the loader will
        try to fetch weather observations and enrich every telemetry record with
        the corresponding weather fields.
    params:
        Extra query parameters forwarded to the Vector endpoint on every
        request (e.g. ``{"limit": 1000}``).
    weather_params:
        Extra query parameters forwarded to the weather endpoint.
    timeout:
        HTTP request timeout in seconds (default 30).
    merge_on:
        Column name used to join telemetry records with weather records.
        Defaults to ``"timestamp"``.
    session:
        Optional :class:`requests.Session` to use.  Useful for injecting
        pre-configured sessions in tests.

    Examples
    --------
    Basic usage::

        from vectorlib import DataLoader

        loader = DataLoader(
            url="http://vector-instance/api/records",
            weather_url="http://weather-api/observations",
        )

        for record in loader:
            print(record)

        df = loader.to_dataframe()
    """

    def __init__(
        self,
        url: str,
        weather_url: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        weather_params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        merge_on: str = "timestamp",
        session: Optional[requests.Session] = None,
    ) -> None:
        self.url = url
        self.weather_url = weather_url
        self.params = params or {}
        self.weather_params = weather_params or {}
        self.timeout = timeout
        self.merge_on = merge_on
        self._session = session or requests.Session()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_records(self) -> List[Dict[str, Any]]:
        """Fetch raw telemetry records from the Vector endpoint."""
        response = self._session.get(
            self.url, params=self.params, timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("data", "records", "results", "items"):
                if key in data and isinstance(data[key], list):
                    return data[key]
        raise ValueError(
            f"Unexpected response format from {self.url}: "
            f"expected a list or a dict containing a list under a known key."
        )

    def _fetch_weather(self) -> List[Dict[str, Any]]:
        """Fetch weather observations. Returns an empty list if no weather URL
        has been configured."""
        if not self.weather_url:
            return []
        response = self._session.get(
            self.weather_url, params=self.weather_params, timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("data", "records", "results", "observations", "items"):
                if key in data and isinstance(data[key], list):
                    return data[key]
        logger.warning("Could not extract weather records from response; skipping merge.")
        return []

    def _merge_weather(
        self,
        telemetry: List[Dict[str, Any]],
        weather: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Left-merge *telemetry* records with *weather* records on ``merge_on``."""
        if not weather:
            return telemetry
        tel_df = pd.DataFrame(telemetry)
        wea_df = pd.DataFrame(weather)
        if self.merge_on not in tel_df.columns or self.merge_on not in wea_df.columns:
            logger.warning(
                "Merge key '%s' not found in both datasets; skipping merge.",
                self.merge_on,
            )
            return telemetry
        merged = tel_df.merge(wea_df, on=self.merge_on, how="left", suffixes=("", "_weather"))
        return merged.to_dict(orient="records")

    # ------------------------------------------------------------------
    # Generator interface
    # ------------------------------------------------------------------

    def _iter_records(self) -> Generator[Dict[str, Any], None, None]:
        """Core generator: fetches, optionally merges, and yields each record."""
        telemetry = self._fetch_records()
        weather = self._fetch_weather()
        records = self._merge_weather(telemetry, weather)
        for record in records:
            yield record

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return self._iter_records()

    # ------------------------------------------------------------------
    # DataFrame export
    # ------------------------------------------------------------------

    def to_dataframe(self) -> pd.DataFrame:
        """Consume the generator and return all records as a
        :class:`pandas.DataFrame`.

        Returns
        -------
        pandas.DataFrame
            A DataFrame where each row corresponds to one telemetry record
            (enriched with weather data when a weather URL was provided).
        """
        records = list(self)
        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records)

    # ------------------------------------------------------------------
    # Alternative constructor: build from an iterable (useful for testing)
    # ------------------------------------------------------------------

    @classmethod
    def from_records(
        cls,
        records: Iterable[Dict[str, Any]],
        weather_records: Optional[Iterable[Dict[str, Any]]] = None,
        merge_on: str = "timestamp",
    ) -> "DataLoader":
        """Create a :class:`DataLoader` backed by in-memory record collections
        instead of remote HTTP endpoints.  Primarily intended for testing and
        offline processing.

        Parameters
        ----------
        records:
            Iterable of telemetry record dicts.
        weather_records:
            Optional iterable of weather record dicts to merge in.
        merge_on:
            Column name used for the merge (default ``"timestamp"``).

        Returns
        -------
        DataLoader
        """
        loader = cls.__new__(cls)
        loader.url = ""
        loader.weather_url = None
        loader.params = {}
        loader.weather_params = {}
        loader.timeout = 30
        loader.merge_on = merge_on
        loader._session = None  # type: ignore[assignment]

        # Pre-compute merged records and store them for iteration.
        tel_list = list(records)
        wea_list = list(weather_records) if weather_records is not None else []
        loader._records = loader._merge_weather(tel_list, wea_list)

        # Override the generator to yield from the pre-computed list.
        def _iter() -> Generator[Dict[str, Any], None, None]:
            yield from loader._records

        loader._iter_records = _iter  # type: ignore[method-assign]
        return loader
