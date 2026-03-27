import pandas as pd
import sys
from pathlib import Path
from .vector_downloader.script import downloadData


class DataDownloader:

    REQUIRED_COLUMNS = {"Adres egeria", "Węzeł", "Vector"}
    DEFAULT_START_RANGE = "2023-01-01 00:00:00"
    DEFAULT_END_RANGE = "2025-12-31 23:59:59"

    @staticmethod
    def _validate(df):
        if not DataDownloader.REQUIRED_COLUMNS.issubset(df.columns):
            raise ValueError(
                "Input must contain columns: 'Adres egeria', 'Węzeł', 'Vector'"
            )

    @staticmethod
    def from_excel(
        excel_path,
        vector_folder,
        start_range=DEFAULT_START_RANGE,
        end_range=DEFAULT_END_RANGE,
        update_packages=False,
    ):
        df = pd.read_excel(excel_path)
        DataDownloader._validate(df)
        DataDownloader._download(
            df,
            vector_folder,
            start_range=start_range,
            end_range=end_range,
            update_packages=update_packages,
        )

    @staticmethod
    def from_csv(
        csv_path,
        vector_folder,
        start_range=DEFAULT_START_RANGE,
        end_range=DEFAULT_END_RANGE,
        update_packages=False,
    ):
        df = pd.read_csv(csv_path)
        DataDownloader._validate(df)
        DataDownloader._download(
            df,
            vector_folder,
            start_range=start_range,
            end_range=end_range,
            update_packages=update_packages,
        )

    @staticmethod
    def from_dict(
        vector_dict,
        vector_folder,
        start_range=DEFAULT_START_RANGE,
        end_range=DEFAULT_END_RANGE,
        update_packages=False,
    ):
        df = pd.DataFrame.from_dict(vector_dict)
        DataDownloader._validate(df)
        DataDownloader._download(
            df,
            vector_folder,
            start_range=start_range,
            end_range=end_range,
            update_packages=update_packages,
        )

    @staticmethod
    def from_pandas(
        df,
        vector_folder,
        start_range=DEFAULT_START_RANGE,
        end_range=DEFAULT_END_RANGE,
        update_packages=False,
    ):
        DataDownloader._validate(df)
        DataDownloader._download(
            df,
            vector_folder,
            start_range=start_range,
            end_range=end_range,
            update_packages=update_packages,
        )

    @staticmethod
    def _download(df, folder, start_range, end_range, update_packages=False):
        print(f"Trying to download {df.shape[0]} vectors to folder '{folder}'...")
        downloadData(
            df,
            folder,
            start_range=start_range,
            end_range=end_range,
            update_packages=update_packages,
        )
