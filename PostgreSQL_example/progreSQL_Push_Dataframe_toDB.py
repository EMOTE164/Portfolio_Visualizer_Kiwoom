import pandas as pd
from sqlalchemy import create_engine

try:
    #데이터 베이스를 연결하고 db를 선택해줌
    engine = create_engine('postgresql://postgres@localhost:9003/stockdb') #'postgresql://'+'POSTGRESQL_USER'+'POSTGRESQL_PASSWORD'+'POSTGRESQL_HOST_IP'+'POSTGRESQL_PORT'+'POSTGRESQL_DATABASE'



    liste_hello = ['hello1', 'hello2']
    liste_world = ['world1', 'world2']
    df = pd.DataFrame(data={'hello': liste_hello, 'world': liste_world})

    # Writing Dataframe to PostgreSQL and replacing table if it already exists
    # helloworld테이블 생성
    df.to_sql(name='helloworld', con=engine, if_exists='replace', index=False)


except Exception as e:
    print("error")
    print(e)