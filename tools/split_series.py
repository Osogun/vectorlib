import pandas as pd
import numpy as np


def split_series(series, bool_mask, max_gap=None, min_length=None):
    """
    Dzieli serię na podserie na podstawie maski boolowskiej.
    Podserie, które są oddzielone przerwami krótszymi niż max_gap są łączone.
    Subserie mogą być również filtrowane na podstawie minimalnej długości min_length.
    Parametry:
    series (pd.Series): Seria do podziału.
    bool_mask (pd.Series): Maska boolowska tej samej długości co series, gdzie True oznacza element należący do podserii.
    max_gap (int, optional): Maksymalna długość przerwy między podserią a następną, która pozwala na ich połączenie. Domyślnie None, co oznacza brak łączenia.
    min_length (int, optional): Minimalna długość podserii do zachowania. Domyślnie None, co oznacza brak filtrowania.
    Zwraca:
    dict: Słownik podserii.
    """
    series = series.copy()
    parts = bool_mask.ne(bool_mask.shift()).cumsum()
    groups = series.groupby(parts)
    valid_groups_ids = set(series.groupby(parts[bool_mask]).groups.keys())
    valid_groups = {}
    last_valid_group = None
    n = 0
    for k, v in groups:
        concated = False
        if k not in valid_groups_ids:
            continue
        if k > 1:
            group_before = groups.get_group(k - 1)
            if k - 1 not in valid_groups_ids:
                if max_gap is not None and len(group_before) <= max_gap:
                    v = pd.concat([group_before, v])
                    if last_valid_group is not None:
                        valid_groups[n - 1] = pd.concat([last_valid_group, v])
                        concated = True
                        last_valid_group = valid_groups[n - 1]
        if concated == False:
            valid_groups[n] = v
            last_valid_group = valid_groups[n]
            n += 1
    if min_length is not None:
        n = 0
        filtered_groups = {}
        for k, v in valid_groups.items():
            if len(v) >= min_length:
                filtered_groups[n] = v
                n += 1
        return filtered_groups
    return valid_groups
