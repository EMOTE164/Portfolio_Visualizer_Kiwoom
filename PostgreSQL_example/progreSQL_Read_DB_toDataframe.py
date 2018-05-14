import pandas as pd
from sqlalchemy import create_engine

try:
    engine = create_engine('postgresql://postgres@localhost:9003/stockdb')#'postgresql://'+'POSTGRESQL_USER'+'POSTGRESQL_PASSWORD'+'POSTGRESQL_HOST_IP'+'POSTGRESQL_PORT'+'POSTGRESQL_DATABASE'

    data = pd.read_sql('SELECT * FROM stock_code.kospi', engine)
    print(data)


except Exception as e:
    print("error")
    print(e)