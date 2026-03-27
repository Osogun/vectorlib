import pandas as pd
from . import functions
import oracledb
import datetime
import time
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


# Funkcja / zadanie które będzie wykonywał wątek
# row = list_tasks[0]
def vector_load(row, ConnectionPool, start_range, end_range, folder, Error, Checked):
    try:
        start = time.time()

        InputID = int(functions.get_inputID_from_number_vector(int(row.loc["Vector"])))
        with ConnectionPool.acquire() as connection:
            df_vector = functions.download_vector_frame(
                InputID, connection, start_range, end_range
            )

        df_vector.to_excel(f'{folder}/{row.loc["Vector"]}.xlsx')

        print(str(round(time.time() - start, 2)), "s")
        Checked.append(int(row.loc["Vector"]))
    except:
        Error.append(int(row.loc["Vector"]))


def downloadData(
    df_tasks,
    folder,
    start_range="2023-01-01 00:00:00",
    end_range="2025-12-31 23:59:59",
    update_packages=False,
):

    #################################################################
    try:
        oracledb.init_oracle_client("C:\instantclient")
    except:
        pass
    #################################################################

    #################################################################
    config_path = Path(__file__).parent / "config.cfg"
    config = json.load(open(str(config_path), "r"))

    ConnectionPool = oracledb.create_pool(
        user=config["Vector"]["User"],
        password=config["Vector"]["Password"],
        dsn=f"{config['Vector']['Host']}:{config['Vector']['Port']}/{config['Vector']['Service']}",  # host:port/service_name
        min=1,  # minimalna liczba połączeń w puli
        max=4,  # maksymalna liczba połączeń
        increment=1,
    )
    #################################################################

    # Do aktualizacji pliku packages.pkl
    if update_packages:
        print("Updating packages.pkl...")
        dsn_tns = oracledb.makedsn(
            config["Vector"]["Host"],
            config["Vector"]["Port"],
            config["Vector"]["Service"],
        )
        connection = oracledb.connect(
            user=config["Vector"]["User"],
            password=config["Vector"]["Password"],
            dsn=dsn_tns,
        )
        functions.update_Data(
            oracledb.connect(
                user=config["Vector"]["User"],
                password=config["Vector"]["Password"],
                dsn=dsn_tns,
            )
        )
        connection.close()

    #################################################################
    killThreads = 0
    # Przygotowanie zadan dla wątków, w tym wypadku 1 wątek bierze do wykonania jede wiersz ramki df_tasks
    list_tasks = []
    [list_tasks.append(row) for index, row in df_tasks.loc[:].iterrows()]

    thread_info = {}

    Error = []
    Checked = []

    # Ilosc zdefiniowanych watkow do wykonywania zadan
    threads = 4
    #################################################################
    with ThreadPoolExecutor(max_workers=threads) as executor:
        # Rozpoczęcie wykonywania zadań przez wątki, każdy wątek bierze jeden wiersz df_task i wykonuje zadanie, po wykonaniu bierze kolejne niewykonane zadanie do zrealizowania
        results = executor.map(
            vector_load,
            list_tasks,
            [ConnectionPool] * len(list_tasks),
            [start_range] * len(list_tasks),
            [end_range] * len(list_tasks),
            [folder] * len(list_tasks),
            [Error] * len(list_tasks),
            [Checked] * len(list_tasks),
        )
    print("Done!")
