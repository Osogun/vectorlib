vector_config = {
    "columns": {
        "UNIT_DATE": "Data odczytu",
        "Id": "Identyfikator",
        "ThermalEnergy": "Energia [GJ]",
        "Volume": "Objętość [m3]",
        "SourceTemp": "Temperatura zasilania [°C]",
        "ReturnTemp": "Temperatura powrotu [°C]",
        "TempDifference": "Różnica temperatur [°C]",
        "FlowVolume": "Przepływ [l/h]",
        "Power": "Moc [kW]",
        "VolumeWM1": "Objętość wodomierza 1 [m3]",
        "VolumeWM2": "Objętość wodomierza 2 [m3]",
    },
    "time_frequency": "h",
    "separator": ";",
    "encoding": "cp1250",
    "decimal_sep": ",",
    "join_method": "left",
}

vector_clone_config = {
    "columns": {
        "UNIT_DATE": "UNIT_DATE",
        "Id": "Identyfikator",
        "ThermalEnergy": "ThermalEnergy",
        "Volume": "Volume",
        "SourceTemp": "SourceTemp",
        "ReturnTemp": "ReturnTemp",
        "TempDifference": "TempDifference",
        "FlowVolume": "FlowVolume",
        "Power": "Power",
        "VolumeWM1": "VolumeWM1",
        "VolumeWM2": "VolumeWM2",
    },
    "time_frequency": "h",
    "separator": ",",
    "encoding": "cp1250",
    "decimal_sep": ".",
    "join_method": "left",
}

vector_config_xls = {
    "columns": {
        "UNIT_DATE": "Data odczytu",
        "Id": "Identyfikator",
        "ThermalEnergy": "Energia [GJ]",
        "Volume": "Objętość [m³]",
        "SourceTemp": "Temperatura zasilania [°C]",
        "ReturnTemp": "Temperatura powrotu [°C]",
        "TempDifference": "Różnica temperatur [°C]",
        "FlowVolume": "Przepływ [l/h]",
        "Power": "Moc [kW]",
        "VolumeWM1": "Objętość wodomierza 1 [m³]",
        "VolumeWM2": "Objętość wodomierza 2 [m³]",
    },
    "time_frequency": "h",
    "separator": ";",
    "encoding": "cp1250",
    "decimal_sep": ",",
    "join_method": "left",
}

abaro_config = {
    "columns": {
        "UNIT_DATE": "Data odczytu",
        "Id": "Numer seryjny",
        "ThermalEnergy": "Energia [GJ]",
        "Volume": "Objętość [m³]",
        "SourceTemp": "Temperatura zasilania [°C]",
        "ReturnTemp": "Temperatura powrotu [°C]",
        "TempDifference": "Różnica temperatur [°C]",
        "FlowVolume": "Przepływ chwilowy [l/h]",
        "Power": "Moc chwilowa [kW]",
        "VolumeWM1": "Objętość wodomierza 1 [m³]",
        "VolumeWM2": "Objętość wodomierza 2 [m³]",
    },
    "time_frequency": "h",
    "separator": ",",
    "encoding": "utf-8",
    "decimal_sep": ".",
    "join_method": "left",
}

weather_Gdansk = {
    "weather_data_path": r"T:\Aplikacje\Pogoda\3_Raporty\Pogoda Gdańsk.xlsx",
    "data_col": 7,  # port_pólnocny (1), reibechowo (4), średnia (7),"
    "index_col": 0,
    "seson_col": 11,
    "skiprows": [0, 1, 2],
    "header": None,
    "sheet_name": "Godzinowe",
}

weather_Tczew = {
    "weather_data_path": r"C:\Users\o.gumowski\OneDrive - Gdańskie Przedsiębiorstwo Energetyki Cieplnej Sp. z o.o\Pulpit\Workspace\ZZZ\Temperatura Tczew\raport_ZAKRES 2026-02-12 141234.xlsx",
    "data_col": 1,
    "index_col": 0,
    "seson_col": 2,
    "skiprows": [0, 1, 2],
    "header": None,
    "sheet_name": "Arkusz1",
}
