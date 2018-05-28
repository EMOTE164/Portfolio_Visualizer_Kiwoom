from sqlalchemy import create_engine
from pandas import Series, DataFrame, read_sql, concat
import operator

#사용자에게 입력받는 데이터
startDate = "20000101"
endDate = "20091230"

initial_money = "1000000"

consider_item__list = ["000020", "000040", "000080"]

timing_period = "5"    # 매매시교체 시기
number_keep = "2"      # 보유할 종목의 수


try:
    items_df_list = []  # 관심종목에 담긴 종목의 데이터들

    #사용자에게 입력받은 값 형변환
    initial_money = int(initial_money)
    timing_period = int(timing_period)
    number_keep = int(number_keep)
    evaluation_balance = initial_money      #보유하고 있는 종목금액 + remain_balance
    remain_balance = initial_money          #매수 가능한 잔고에 남아있는 금액

    #DB연결
    engine = create_engine('postgresql://postgres@localhost:9003/stockdb')#'postgresql://'+'POSTGRESQL_USER'+'POSTGRESQL_PASSWORD'+'POSTGRESQL_HOST_IP'+'POSTGRESQL_PORT'+'POSTGRESQL_DATABASE'

    #DB로부터 consider_item_list에 들어있는 종목 데이터를 읽어서 items_df_list에 추가한다.
    for i in range(0, len(consider_item__list)):
        temp_df = read_sql("SELECT * FROM stock_kospi.daily_price where code = \'"+ consider_item__list[i] +"\' and date >= \'" + startDate + "\' and date <= \'" + endDate + "\'" + " order by date", engine)
        items_df_list.append(temp_df)

    #데이터 길이가 0인 종목은 리스트에서 제거해버린다.
    for itemNumber in range(0, len(items_df_list)):
        if(len(items_df_list[itemNumber]) == 0):
            del items_df_list[itemNumber]

    # 가장 기간이 긴 종목의 데이터프레임 선별(데이터 길이를 모두 같게 해주기전 기준이될 애를 고르기위해서)
    indexOflongestItem = 0
    for itemNumber in range(0, len(items_df_list)):
        if (len(items_df_list[indexOflongestItem]) < len(items_df_list[itemNumber])):
            indexOflongestItem = itemNumber

    # 데이터의 길이를 동일하게 맞춰줌
    for itemNumber in range(0, len(items_df_list)):
        if (itemNumber != indexOflongestItem and len(items_df_list[itemNumber]) != len(items_df_list[indexOflongestItem])):
            minDate = items_df_list[itemNumber]["date"].min()
            maxDate = items_df_list[itemNumber]["date"].max()
            minIndex = 0
            maxIndex = 0
            for i in range(0, len(items_df_list[indexOflongestItem])):
                if (minDate == items_df_list[indexOflongestItem].loc[i][1]):
                    minIndex = i
                elif (maxDate == items_df_list[indexOflongestItem].loc[i][1]):
                    maxIndex = i
                    break

            temp_df = DataFrame(items_df_list[indexOflongestItem].ix[0:minIndex - 1, "date"])
            temp_df["code"] = None
            temp_df["open"] = None
            temp_df["low"] = None
            temp_df["high"] = None
            temp_df["close"] = None
            temp_df["count"] = None
            temp_df["money"] = None
            temp_df["timing_period_benefit"] = None
            temp_df = temp_df[['code', 'date', 'open', 'low', 'high', 'close', 'count', 'money']]  # column순서 변경
            items_df_list[itemNumber] = concat([temp_df, items_df_list[itemNumber]], axis=0)  # 프레임 위아래로 합치기

            temp_df = DataFrame(items_df_list[indexOflongestItem].ix[maxIndex + 1:len(items_df_list[indexOflongestItem]) - 1,"date"])
            temp_df["code"] = None
            temp_df["open"] = None
            temp_df["low"] = None
            temp_df["high"] = None
            temp_df["close"] = None
            temp_df["count"] = None
            temp_df["money"] = None
            temp_df["timing_period_benefit"] = None
            temp_df = temp_df[['code', 'date', 'open', 'low', 'high', 'close', 'count', 'money']]  # column순서 변경
            items_df_list[itemNumber] = concat([temp_df, items_df_list[itemNumber]], axis=0)  # 프레임 위아래로 합치기

            items_df_list[itemNumber] = items_df_list[itemNumber].sort_values(by="date")  # 날짜를 기준으로 데이터 정렬
            items_df_list[itemNumber] = items_df_list[itemNumber].reset_index(drop=True)  # index 초기화


    #items_df_list에 들어있는 df를 하나씩 가져와서 계산한 benefit을 column으로 추가해준다.
    for itemNumber in range(0, len(items_df_list)):
        item = items_df_list[itemNumber]
        item["timing_period_benefit"] = None    #timing_period_benefit column을 추가
        for i in range(0, len(item)):
            if ((i + timing_period) % timing_period == 0 and item.loc[i][5] != None):
                if (i == 0):
                    beforePrice = item.loc[i][5]
                    # print(str(i) + " beforePrice : " + str(beforePrice))
                else:
                    afterPrice = item.loc[i][5]
                    # print(str(i) + " afterPrice : " + str(afterPrice))

                    benefit = (afterPrice - beforePrice) / beforePrice * 100
                    benefit = round(benefit, 2)  # 소수점 아래 2자리까지만 남기게 반올림
                    # print("benefit : " + str(benefit))
                    item.ix[i, 8] = benefit  # None -> 값 추가

                    # 연산진행
                    beforePrice = item.loc[i][5]
                    # print(str(i) + " beforePrice : " + str(beforePrice))

    #과거 데이터에 대하여 매수, 매도 진행
    holding_item_indexs=[]   #보유중인 아이템의 인덱스
    tradeDetails_df = DataFrame(columns = ("date", "code", "action", "price", "volume", "total_money")) # 매수, 매도 거래내역이 저장되는 변수
    dailyEvaluationValance_df = DataFrame(columns = ("date", "evaluation_money"))   #일별로 평가금액이 얼마인지가 저장되는 변수
    for i in range(0, len(items_df_list[0])):
        currentDay = items_df_list[0].loc[i][1]
        if(items_df_list[0].loc[i][8] != None):
            if(len(holding_item_indexs) != 0):   # 보유중인 종목이 있다면 매도처리
                for j in range(0, len(holding_item_indexs)):
                    date = currentDay
                    code = items_df_list[holding_item_indexs[j][0]].loc[i][0]
                    action = "sell"
                    price = items_df_list[holding_item_indexs[j][0]].loc[i][5]
                    volume = tradeDetails_df.loc[len(tradeDetails_df)-2][4]
                    total_money = price * volume
                    remain_balance = remain_balance + total_money
                    rows = [date, code, action, price, volume, total_money]     #row추가
                    tradeDetails_df.loc[len(tradeDetails_df)] = rows
                holding_item_indexs = [] #reset
            #매수처리
            ableMoneyPerOneItem = remain_balance / number_keep
            benefit_compare_list = []
            for itemNumber in range(0, len(items_df_list)):
                if(items_df_list[itemNumber].loc[i][8] != None):
                    benefit_compare_list.append((itemNumber, float(items_df_list[itemNumber].loc[i][8])))
                    benefit_compare_list = sorted(benefit_compare_list, key=lambda x: x[1], reverse=True) # 수익률 순으로 정렬
            for j in range(0, number_keep):
                date = currentDay
                code = items_df_list[benefit_compare_list[j][0]].loc[i][0]
                action = "buy"
                price = items_df_list[benefit_compare_list[j][0]].loc[i][5]
                volume = int(ableMoneyPerOneItem / price)
                total_money = price * volume
                remain_balance = remain_balance - total_money
                rows = [date, code, action, price, volume, total_money]
                tradeDetails_df.loc[len(tradeDetails_df)] = rows            #row추가
                holding_item_indexs.append((benefit_compare_list[j][0],volume))

        #매일 여기서 자산이 얼마인지 확인.
        if(len(holding_item_indexs) == 0):
            evaluation_balance = remain_balance
        else:
            holding_money = 0
            for j in range(0,len(holding_item_indexs)):
                currentPrice = items_df_list[holding_item_indexs[j][0]].loc[i][5]
                volume = holding_item_indexs[j][1]
                holding_money = holding_money + (currentPrice * volume)
            evaluation_balance = remain_balance + holding_money
        rows = [currentDay, evaluation_balance]
        dailyEvaluationValance_df.loc[len(dailyEvaluationValance_df)] = rows    #row추가

    print(tradeDetails_df)
    print(dailyEvaluationValance_df)



except Exception as e:
    print("error")
    print(e)