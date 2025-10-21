from sqlalchemy import create_engine
import pandas as pd
import os
from datetime import datetime

sqlite_path = "/home/jack/git/Python/Projects/theweather/containers/container_data/api-server/db/api-server.db"
output_dir = "./db_backup/parquet"
os.makedirs(output_dir, exist_ok=True)
date_str = datetime.now().strftime("%Y-%m-%d")

engine = create_engine(f"sqlite:///{sqlite_path}")

tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", engine)[
    "name"
].tolist()

chunk_size = 10000

for table in tables:
    sql_query = f"SELECT * FROM {table}"
    batch_num = 0
    for chunk in pd.read_sql(sql_query, engine, chunksize=chunk_size):
        batch_num += 1
        filename = f"{date_str}_{table}_part{batch_num}.parquet"
        filepath = os.path.join(output_dir, filename)
        chunk.to_parquet(filepath, index=False)
        print(f"Exported chunk {batch_num} of table {table} to {filepath}")
