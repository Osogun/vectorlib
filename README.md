# vectorlib
Narzędzia do przetwarzania i analizy danych telemetrycznych z systemu Vector.

## Instalacja

```bash
pip install git+https://github.com/Osogun/vectorlib.git
```

## API

```python
from vectorlib import DataLoader, DataCleaner
```

### DataLoader

Generator do pobierania danych z Vectora / Klona Vectora, łączenia z danymi pogodowymi i eksportu do DataFrame.

```python
loader = DataLoader(
    url="http://vector-instance/api/records",
    weather_url="http://weather-api/observations",  # opcjonalnie
    params={"limit": 1000},
    merge_on="timestamp",
)

# iteracja po rekordach
for record in loader:
    print(record)

# eksport do DataFrame
df = loader.to_dataframe()
```

Do testów / pracy offline dostępny jest alternatywny konstruktor `from_records`:

```python
loader = DataLoader.from_records(records, weather_records, merge_on="timestamp")
df = loader.to_dataframe()
```

### DataCleaner

Klasa statyczna z wbudowanymi narzędziami do czyszczenia serii danych.

```python
import pandas as pd
from vectorlib import DataCleaner

s = pd.Series([1.0, None, 3.0, 1000.0, 5.0])

# Uzupełnianie brakujących wartości
clean = DataCleaner.fill_missing(s, method="mean")   # mean | median | mode | ffill | bfill | interpolate | zero

# Usuwanie wartości odstających
clean = DataCleaner.remove_outliers(s, method="iqr", threshold=1.5)  # iqr | zscore

# Normalizacja
clean = DataCleaner.normalize(s, method="minmax")  # minmax | zscore

# Wygładzanie
clean = DataCleaner.smooth(s, window=5, method="rolling_mean")  # rolling_mean | ewm

# Usuwanie duplikatów
df_clean = DataCleaner.remove_duplicates(df, keep="first")

# Usuwanie wartości null
clean = DataCleaner.drop_nulls(s)

# Konwersja typów
clean = DataCleaner.to_numeric(s, errors="coerce")
clean = DataCleaner.to_datetime(s)

# Przycinanie wartości
clean = DataCleaner.clip(s, lower=0.0, upper=100.0)
```

## Testy

```bash
pip install -e ".[dev]"
pytest tests/
```

