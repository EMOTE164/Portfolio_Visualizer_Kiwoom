#상대적 모멘텀 투자 백테스팅
from sqlalchemy import create_engine
from pandas import DataFrame, read_sql, concat
import json




startDate = "20160101"
endDate = "20160301"

itemCode = "000020"



try:
    #DB연결
    engine = create_engine('postgresql://postgres@localhost:9003/stockdb')#'postgresql://'+'POSTGRESQL_USER'+'POSTGRESQL_PASSWORD'+'POSTGRESQL_HOST_IP'+'POSTGRESQL_PORT'+'POSTGRESQL_DATABASE'

    item_df = read_sql("SELECT date, close FROM stock_kospi.daily_price where code = \'" + itemCode + "\' and date >= \'" + startDate + "\' and date <= \'" + endDate + "\'" + " order by date", engine)

    #Json변환
    date_list = []
    price_list = []
    for i in range(0, len(item_df)):
        date_list.append(str(item_df.loc[i][0]))
        price_list.append(str(item_df.loc[i][1]))

    data = {}
    data["date"] = date_list
    data["evaluation_money"] = price_list
    json_data = json.dumps(data, ensure_ascii=False)
    print(json_data)

except Exception as e:
    print("error")
    print(e)
