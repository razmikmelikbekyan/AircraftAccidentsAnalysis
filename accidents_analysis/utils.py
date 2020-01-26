import json

import mysql.connector
import pandas as pd


def sql_table_to_pandas(db_config_path: str, table_name: str) -> pd.DataFrame:
    with open(db_config_path, 'r') as infile:
        db_config = json.load(infile)

    cnx = mysql.connector.connect(**db_config)
    return pd.read_sql(f"SELECT * FROM {table_name}", cnx)
