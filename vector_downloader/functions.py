# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 10:30:10 2023

@author: m.gorski
"""

import datetime as dt
import pickle
import pandas as pd
import warnings
import oracledb
from pathlib import Path


def update_Data(connection):
    packages = {}

    print("Trwa aktualizacja pakietów. Może potrwać to nawet 30min.")

    print("1/6 | Aktualizacja tablicy definicji konfiguracji danych")
    query = """SELECT INPUT_ID, INPUT_DATA_CONFIG_ID, max(UNIT_DATE), min(UNIT_DATE)
    FROM GPEC2.INPUT_DATA_HISTORY 
    GROUP BY INPUT_ID, INPUT_DATA_CONFIG_ID"""
    packages["INPUT_DATA_HISTORY-definition"] = pd.read_sql(query, con=connection)

    print("2/6 | Aktualizacja tablicy informacji o urządzeniach")
    query = "SELECT * FROM GPEC2.INPUT_DEVICE"

    packages["INPUT_DATA_DEVICE-information"] = pd.read_sql(query, con=connection)

    print("3/6 | Aktualizacja tablicy konfiguracji o odczytach")
    query = "SELECT * FROM GPEC2.IO_READ_CONFIG"
    packages["IO_READ_CONFIG"] = pd.read_sql(query, con=connection)

    print("4/6 | Aktualizacja tablicy mapowań urządzeń")
    query = "SELECT * FROM GPEC2.LOGICAL_DEV_IO_READ_CFG"
    packages["LOGICAL_DEVICE_MAPPING"] = pd.read_sql(query, con=connection)

    print("5/6 | Aktualizacja tablicy konfiguracji danych IRC")
    query = "SELECT * FROM GPEC2.INPUT_DATA_CONFIG_I_R_C"
    packages["INPUT_DATA_CONFIG_I_R_C"] = pd.read_sql(query, con=connection)

    print("6/6 | Aktualizacja tablicy informacji o modułach Vector")
    query = "SELECT * FROM GPEC2.input"
    packages["INPUT_MODULE_INFORMATION"] = pd.read_sql(query, con=connection)

    packages["date"] = dt.datetime.now()

    packages_path = Path(__file__).parent / "packages.pkl"
    pickle.dump(packages, open(packages_path, "wb+"))


def load_pre_data():
    warnings.filterwarnings("ignore")

    try:
        oracledb.init_oracle_client("C:\instantclient")
    except:
        pass

    hostname = "vectdb-isc.gpec.corp"
    username = "GPEC_ISC"
    password = "K?4a=Lt$"
    service = "vecdbisc"
    port = 1521
    dsn_tns = oracledb.makedsn(hostname, port, service)

    connection = oracledb.connect(user=username, password=password, dsn=dsn_tns)

    # Ścieżka absolutna do packages.pkl
    pkg_path = Path(__file__).parent / "packages.pkl"
    return pickle.load(open(str(pkg_path), "rb+"))


global packages
packages = load_pre_data()


def getLayoutName(circuit_name):
    try:
        return (
            "_"
            + (
                set(circuit_name.split("_"))
                & set(
                    [
                        "RegMain",
                        "RegCO",
                        "RegCW",
                        "REG",
                        "CO",
                        "CO1",
                        "CO2",
                        "CO3",
                        "CO4",
                        "CW",
                        "CWU",
                        "CWU1",
                        "CWU2",
                        "CWU3",
                        "PRE",
                        "WD",
                        "Circuit1",
                        "Circuit2",
                        "Circuit3",
                        "CircuitCW",
                    ]
                )
            ).pop()
        )
    except:
        return ""


def download_vector_frame(input_id, connection, start_range, end_range):

    # Debugowanie funkcji
    """
    input_id = 17827
    start_range = '2024-01-01 00:00'
    end_range = '2024-01-31 23:59'
    """
    query = f"""SELECT *
                FROM  GPEC2.INPUT_DATA_HISTORY
                WHERE INPUT_ID = {input_id}
                    AND UNIT_DATE  >= TO_DATE('{start_range}', 'YYYY-MM-DD hh24:mi:ss')
                    AND UNIT_DATE  <= TO_DATE('{end_range}', 'YYYY-MM-DD hh24:mi:ss')
            """

    Persist_type = {0: "VALN", 1: "VALD", 2: "VALS", 3: "VALC"}

    df_read_SQL = pd.read_sql(query, con=connection)
    if df_read_SQL.empty != True:
        try:
            df_read_SQL.loc[:, "Numer modułu"] = str(
                packages["INPUT_MODULE_INFORMATION"]
                .loc[packages["INPUT_MODULE_INFORMATION"].ID == input_id]
                .UNIT_ID.values[0]
            )
            df_read_SQL.loc[:, "Moduł aktywny"] = str(
                packages["INPUT_MODULE_INFORMATION"]
                .loc[packages["INPUT_MODULE_INFORMATION"].ID == input_id]
                .IS_ACTIVE.values[0]
            )
            df_read_SQL.loc[:, "Identyfikator"] = str(
                packages["INPUT_DATA_DEVICE-information"]
                .loc[
                    packages["INPUT_DATA_DEVICE-information"]
                    .sort_values("ID")
                    .loc[:, "INPUT_ID"]
                    == input_id,
                    "IDENTIFIER",
                ]
                .iloc[0]
            )
            df_read_SQL.loc[:, "Urządzenie aktywne"] = str(
                packages["INPUT_DATA_DEVICE-information"]
                .loc[
                    packages["INPUT_DATA_DEVICE-information"]
                    .sort_values("ID")
                    .loc[:, "INPUT_ID"]
                    == input_id,
                    "IS_ACTIVE",
                ]
                .iloc[0]
            )
            device = (
                packages["INPUT_DATA_DEVICE-information"]
                .loc[
                    packages["INPUT_DATA_DEVICE-information"]
                    .sort_values("ID")
                    .loc[:, "INPUT_ID"]
                    == input_id
                ]
                .iloc[0]
            )

            # Ramka tymczasowa, ustawienie podstawowych kolumn
            df_temp = df_read_SQL.loc[
                :,
                [
                    "Identyfikator",
                    "Urządzenie aktywne",
                    "Numer modułu",
                    "Moduł aktywny",
                    "INPUT_ID",
                    "INPUT_DATA_CONFIG_ID",
                    "UNIT_DATE",
                ],
            ]
            for id_idc in df_temp.INPUT_DATA_CONFIG_ID.unique():
                # Wyszukanie ustawień dla danego urządzenia
                device_data_config = (
                    packages["IO_READ_CONFIG"]
                    .set_index("ID")
                    .loc[
                        packages["INPUT_DATA_CONFIG_I_R_C"]
                        .loc[
                            packages["INPUT_DATA_CONFIG_I_R_C"].INPUT_DATA_CONFIG_ID
                            == id_idc
                        ]
                        .IO_READ_CONFIG_ID.values
                    ]
                )
                device_data_config = device_data_config.merge(
                    packages["LOGICAL_DEVICE_MAPPING"]
                    .loc[
                        packages["LOGICAL_DEVICE_MAPPING"].IO_READ_CONFIG_ID.isin(
                            device_data_config.index
                        )
                    ]
                    .set_index("IO_READ_CONFIG_ID")
                    .LOGICAL_DEVICE_ID,
                    left_index=True,
                    right_index=True,
                )
                device_data_config.loc[:, "LOGICAL_DEVICE_ID_sufix"] = (
                    device_data_config.loc[:, "LOGICAL_DEVICE_ID"].apply(getLayoutName)
                )

                # Dodanie do ramki danych, kolumny z nazwą urządzenia
                try:
                    df_temp.loc[df_temp.INPUT_DATA_CONFIG_ID == id_idc, "DEVICE_ID"] = (
                        df_temp.loc[
                            df_temp.INPUT_DATA_CONFIG_ID == id_idc, "DEVICE_ID"
                        ].fillna(device_data_config.IO_DEVICE_ID.values[0])
                    )
                except:
                    df_temp.loc[df_temp.INPUT_DATA_CONFIG_ID == id_idc, "DEVICE_ID"] = (
                        device_data_config.IO_DEVICE_ID.values[0]
                    )

                # Dla każdego wyszukanego parametru, znajduję odpowiednią kolumnęw w ramce danych, odpowiednio ją nazwya i dodaje ją do ramki tymczasowej
                for index, row in device_data_config.iterrows():
                    # Zdefiniowanie nazwy kolumny pod którą jest zapisany dany parametr
                    column_name = str(Persist_type[row.PERSIST_TYPE]) + str(
                        row.PERSIST_COLUMN
                    )
                    try:
                        # Dla regulatorów, nazwa parametru jest podzielona dodatkowo na układ (CO1/CO2/CWU/PRE/CW itd.)
                        if ("REGULATOR" in str(device.CUSTOM_LOGICAL_DEVICE_ID)) | (
                            len(str(df_read_SQL.loc[:, "Identyfikator"].iloc[0])) < 7
                        ):
                            df_temp.loc[
                                df_temp.INPUT_DATA_CONFIG_ID == id_idc,
                                str(row.DATA_TYPE_ID) + row.LOGICAL_DEVICE_ID_sufix,
                            ] = df_temp.loc[
                                df_temp.INPUT_DATA_CONFIG_ID == id_idc,
                                str(row.DATA_TYPE_ID) + row.LOGICAL_DEVICE_ID_sufix,
                            ].fillna(
                                df_read_SQL.loc[
                                    df_read_SQL.INPUT_DATA_CONFIG_ID == id_idc,
                                    column_name,
                                ]
                            )
                        else:
                            df_temp.loc[
                                df_temp.INPUT_DATA_CONFIG_ID == id_idc,
                                str(row.DATA_TYPE_ID),
                            ] = df_temp.loc[
                                df_temp.INPUT_DATA_CONFIG_ID == id_idc,
                                str(row.DATA_TYPE_ID),
                            ].fillna(
                                df_read_SQL.loc[
                                    df_read_SQL.INPUT_DATA_CONFIG_ID == id_idc,
                                    column_name,
                                ]
                            )

                    except:
                        if ("REGULATOR" in str(device.CUSTOM_LOGICAL_DEVICE_ID)) | (
                            len(str(df_read_SQL.loc[:, "Identyfikator"].iloc[0])) < 7
                        ):
                            df_temp.loc[
                                df_temp.INPUT_DATA_CONFIG_ID == id_idc,
                                str(row.DATA_TYPE_ID) + row.LOGICAL_DEVICE_ID_sufix,
                            ] = df_read_SQL.loc[
                                df_read_SQL.INPUT_DATA_CONFIG_ID == id_idc, column_name
                            ]
                        else:
                            df_temp.loc[
                                df_temp.INPUT_DATA_CONFIG_ID == id_idc,
                                str(row.DATA_TYPE_ID),
                            ] = df_read_SQL.loc[
                                df_read_SQL.INPUT_DATA_CONFIG_ID == id_idc, column_name
                            ]
            return df_temp
        except:
            # print(r'         |________Błąd podczas przetwarzania ramki')
            return pd.DataFrame()
            pass
    else:
        # print(r'         |________Brak pomiarów')
        return pd.DataFrame()


def get_inputID_from_number_vector(number_vector):
    # return packages['INPUT_DATA_DEVICE-information'].loc[packages['INPUT_DATA_DEVICE-information'].loc[:, 'IDENTIFIER'] == str(number_vector), 'INPUT_ID'].iloc[-1]
    return (
        packages["INPUT_DATA_DEVICE-information"]
        .sort_values(by=["LAST_CORRECT_READ_DATE", "ACTIVATION_AT"], ascending=False)
        .loc[
            packages["INPUT_DATA_DEVICE-information"].loc[:, "IDENTIFIER"]
            == str(number_vector),
            "INPUT_ID",
        ]
        .iloc[0]
    )


def get_inputID_from_number_module(number_module, input_pos):
    return (
        packages["INPUT_MODULE_INFORMATION"]
        .loc[
            (packages["INPUT_MODULE_INFORMATION"].UNIT_ID == int(number_module))
            & (packages["INPUT_MODULE_INFORMATION"].INPUT_POS == input_pos)
        ]
        .ID.iloc[0]
    )
