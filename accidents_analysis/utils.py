import json
from typing import Iterable, Tuple

import editdistance
import mysql.connector
import pandas as pd


def sql_table_to_pandas(db_config_path: str, table_name: str) -> pd.DataFrame:
    with open(db_config_path, 'r') as infile:
        db_config = json.load(infile)

    cnx = mysql.connector.connect(**db_config)
    return pd.read_sql(f"SELECT * FROM {table_name}", cnx)


def str2str_match_ratio(s_1: str, s_2: str) -> float:
    """Calculates 2 string match ratio using given method."""

    def _process(s: str) -> str:
        if not s:
            return ''
        return ' '.join(s.split()).replace('.', '')

    s_1, s_2 = _process(s_1), _process(s_2)

    if not s_1 or not s_2:
        return 0.

    return 1 - editdistance.eval(s_1, s_2) / max(len(s_1), len(s_2))


def str2iter_match_ratio(s: str, iterable_s: Iterable) -> Tuple[str, float]:
    """
    Find the item from the given iterable of strings which has highest match ratio comparing with
    the base string and return the best match and it's match ratio.
    """
    if all(False for _ in iterable_s):
        return '', 0.

    matches = [(x, str2str_match_ratio(s, x)) for x in iterable_s]
    matches.sort(key=lambda x: x[1])
    return matches[-1]
