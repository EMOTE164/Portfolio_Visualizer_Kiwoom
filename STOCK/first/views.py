from django.shortcuts import render

import psycopg2
import json
import base64

# chartdata_graph
from sqlalchemy import create_engine
from pandas import DataFrame, read_sql, concat

# Create your views here.
def index(request):

    host = "localhost"
    user = "postgres"
    dbname = "stockdb"  # 사용할 데이터베이스 이름
    password = "emote164"  # 설치할 때 지정한 것
    port = "9003"  # 설치할 때 지정할 것

    conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host, user, dbname, password, port)

    try:
        # 데이터 베이스를 연결하고 db를 선택해줌
        conn = psycopg2.connect(conn_string)
        print("연결성공")

        cursor = conn.cursor()

        cursor.execute("select * FROM stock_code.kospi;")

        result = cursor.fetchall()  # type : list
        for lists in result:
            print(lists);
        result[0][0];


        print(result[0][0])


    except Exception as e:
        print("error")
        print(e)

    conn.commit()  # 이게 없으면 실제로 반영이 안됨.
    cursor.close()
    conn.close()

    return render(request,'test_3.html')

def chartdata(request):
    host = "localhost"
    user = "postgres"
    dbname = "stockdb"  # 사용할 데이터베이스 이름
    password = "emote164"  # 설치할 때 지정한 것
    port = "9003"  # 설치할 때 지정할 것

    conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host, user, dbname, password, port)

    try:
        # 데이터 베이스를 연결하고 db를 선택해줌
        conn = psycopg2.connect(conn_string)
        print("연결성공")

        cursor = conn.cursor()

        cursor.execute("select * FROM stock_code.kospi;")

        result = cursor.fetchall()  # type : list
        # print(result[0][0])

        # DB에 있는 주식 종목코드와 이름을 JSON Array로 만들어서 리턴하는 코드.. format은 다음과 같음.
        # [ {"code":"종목코드", "name":"이름"}, {"code":"종목코드", "name":"이름"}, ..... ]
        datalist = []
        for element in result:
            if element[0] != '':
                data = {}
                data["code"] = element[0]
                data["name"] = element[1]
                data["odate"] = element[2]
                data["rdate"] = element[3]
                # json_string_data = json.dumps(data, ensure_ascii=False)
                # json_object_data = json.loads(json_string_data)
                # datalist.append(json_object_data)
                datalist.append(data)
        json_data = json.dumps(datalist, ensure_ascii=False)
        print(json_data)

    except Exception as e:
        print("error")
        print(e)

    conn.commit()  # 이게 없으면 실제로 반영이 안됨.
    cursor.close()
    conn.close()
    #json_data = json_data.encode('utf-8')
    #json_data = base64.b64encode(json_data)

    # product_chartdata.html 파일 가보면 urlencode 옵션 줬음. HTML 특수문자코드때문.
    return render(request,'product_chartdata.html', {'json_data': json_data})

def chartdata_graph(request):
    # 사용자에게 입력받는 데이터    01/01/2016 - 01/31/2016 // 300,000 // 3 // 10 // 000070,000075
    startenddate = request.GET["startenddate"]
    initial_money = request.GET["initial_money"]#"1000000"
    number_keep = request.GET["number_keep"]#"2"  # 보유할 종목의 수
    timing_period = request.GET["timing_period"]#"5"  # 매매시교체 주기
    consider_item__list = request.GET["consider_item__list"]#["000020", "000040", "000080"]

    forStartDate = startenddate.replace(' ', '').split('-')[0].split('/')
    forEndDate = startenddate.replace(' ', '').split('-')[1].split('/')
    startDate = forStartDate[2] + forStartDate[0] + forStartDate[1]
    endDate = forEndDate[2] + forEndDate[0] + forEndDate[1]

    initial_money = initial_money.replace(',', '')
    consider_item__list = consider_item__list.split(',')

    print(startDate + "//" + endDate + "//" + initial_money + "//" + number_keep + "//" + timing_period + "//" + str(consider_item__list))
    #return render(request, 'product_chartdata_graph.html')

    try:
        items_df_list = []  # 관심종목에 담긴 종목의 데이터들

        # 사용자에게 입력받은 값 형변환
        initial_money = int(initial_money)
        timing_period = int(timing_period)
        number_keep = int(number_keep)
        evaluation_balance = initial_money  # 보유하고 있는 종목금액 + remain_balance
        remain_balance = initial_money  # 매수 가능한 잔고에 남아있는 금액
        mdd = 0
        bestBenefitAtDay = 0
        worstBenefitAtDay = 0
        totalBenefit = 0

        # DB연결
        engine = create_engine(
            'postgresql://postgres@localhost:9003/stockdb')  # 'postgresql://'+'POSTGRESQL_USER'+'POSTGRESQL_PASSWORD'+'POSTGRESQL_HOST_IP'+'POSTGRESQL_PORT'+'POSTGRESQL_DATABASE'

        # DB로부터 consider_item_list에 들어있는 종목 데이터를 읽어서 items_df_list에 추가한다.
        for i in range(0, len(consider_item__list)):
            temp_df = read_sql("SELECT * FROM stock_kospi.daily_price where code = \'" + consider_item__list[
                i] + "\' and date >= \'" + startDate + "\' and date <= \'" + endDate + "\'" + " order by date", engine)
            items_df_list.append(temp_df)

        # 데이터 길이가 0인 종목은 리스트에서 제거해버린다.
        for itemNumber in range(0, len(items_df_list)):
            if (len(items_df_list[itemNumber]) == 0):
                del items_df_list[itemNumber]

        # 가장 기간이 긴 종목의 데이터프레임 선별(데이터 길이를 모두 같게 해주기전 기준이될 애를 고르기위해서)
        indexOflongestItem = 0
        for itemNumber in range(0, len(items_df_list)):
            if (len(items_df_list[indexOflongestItem]) < len(items_df_list[itemNumber])):
                indexOflongestItem = itemNumber

        # 데이터의 길이를 동일하게 맞춰줌
        for itemNumber in range(0, len(items_df_list)):
            if (itemNumber != indexOflongestItem and len(items_df_list[itemNumber]) != len(
                    items_df_list[indexOflongestItem])):
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

                temp_df = DataFrame(
                    items_df_list[indexOflongestItem].ix[maxIndex + 1:len(items_df_list[indexOflongestItem]) - 1,
                    "date"])
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

        # items_df_list에 들어있는 df를 하나씩 가져와서 계산한 benefit을 column으로 추가해준다.
        for itemNumber in range(0, len(items_df_list)):
            item = items_df_list[itemNumber]
            item["timing_period_benefit"] = None  # timing_period_benefit column을 추가
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

        # 과거 데이터에 대하여 매수, 매도 진행
        holding_item_indexs = []  # 보유중인 아이템의 인덱스
        tradeDetails_df = DataFrame(
            columns=("date", "code", "action", "price", "volume", "total_money"))  # 매수, 매도 거래내역이 저장되는 변수
        dailyEvaluationValance_df = DataFrame(
            columns=("date", "evaluation_money", "variability"))  # 일별로 평가금액이 얼마인지가 저장되는 변수
        for i in range(0, len(items_df_list[0])):
            currentDay = items_df_list[0].loc[i][1]
            if (items_df_list[0].loc[i][8] != None):
                if (len(holding_item_indexs) != 0):  # 보유중인 종목이 있다면 매도처리
                    for j in range(0, len(holding_item_indexs)):
                        date = currentDay
                        code = items_df_list[holding_item_indexs[j][0]].loc[i][0]
                        action = "sell"
                        price = items_df_list[holding_item_indexs[j][0]].loc[i][5]
                        volume = holding_item_indexs[j][1]
                        total_money = price * volume
                        remain_balance = remain_balance + total_money
                        rows = [date, code, action, price, volume, total_money]  # row추가
                        tradeDetails_df.loc[len(tradeDetails_df)] = rows
                    holding_item_indexs = []  # reset
                # 매수처리
                ableMoneyPerOneItem = remain_balance / number_keep
                benefit_compare_list = []
                for itemNumber in range(0, len(items_df_list)):
                    if (items_df_list[itemNumber].loc[i][8] != None):
                        benefit_compare_list.append((itemNumber, float(items_df_list[itemNumber].loc[i][8])))
                        benefit_compare_list = sorted(benefit_compare_list, key=lambda x: x[1], reverse=True)  # 수익률 순으로 정렬
                if (len(benefit_compare_list) > number_keep):
                    k = number_keep
                else:
                    k = len(benefit_compare_list)

                for j in range(0, k):
                    date = currentDay
                    code = items_df_list[benefit_compare_list[j][0]].loc[i][0]
                    action = "buy"
                    price = items_df_list[benefit_compare_list[j][0]].loc[i][5]
                    volume = int(ableMoneyPerOneItem / price)
                    if (volume > 0):
                        total_money = price * volume
                        remain_balance = remain_balance - total_money
                        rows = [date, code, action, price, volume, total_money]
                        tradeDetails_df.loc[len(tradeDetails_df)] = rows  # row추가
                        holding_item_indexs.append((benefit_compare_list[j][0], volume))

            # 매일 여기서 자산이 얼마인지 확인.
            variability = 0.0
            if (len(holding_item_indexs) == 0):
                evaluation_balance = remain_balance
            else:
                holding_money = 0
                for j in range(0, len(holding_item_indexs)):
                    currentPrice = items_df_list[holding_item_indexs[j][0]].loc[i][5]
                    volume = holding_item_indexs[j][1]
                    holding_money = holding_money + (currentPrice * volume)
                evaluation_balance = remain_balance + holding_money

                if (len(dailyEvaluationValance_df) != 0):
                    yesterdayEB = dailyEvaluationValance_df.loc[len(dailyEvaluationValance_df) - 1][1]
                    variability = round(float((evaluation_balance - yesterdayEB) / yesterdayEB) * 100, 2)
                    if (len(dailyEvaluationValance_df) == 1):
                        bestBenefitAtDay = variability
                        worstBenefitAtDay = variability
                    else:
                        if (bestBenefitAtDay < variability):
                            bestBenefitAtDay = variability
                        if (worstBenefitAtDay > variability):
                            worstBenefitAtDay = variability
            rows = [currentDay, evaluation_balance, str(variability)]
            dailyEvaluationValance_df.loc[len(dailyEvaluationValance_df)] = rows  # row추가

        for i in range(0, len(tradeDetails_df)):
            print(tradeDetails_df.loc[i][0], tradeDetails_df.loc[i][1], tradeDetails_df.loc[i][2],
                  tradeDetails_df.loc[i][3], tradeDetails_df.loc[i][4])

        for i in range(0, len(dailyEvaluationValance_df)):
            print(dailyEvaluationValance_df.loc[i][0], dailyEvaluationValance_df.loc[i][1],
                  dailyEvaluationValance_df.loc[i][2])

        # MDD계산
        previousPeakPrice = 0
        optimumPrice = 0

        for i in range(len(dailyEvaluationValance_df)):
            currentPrice = dailyEvaluationValance_df.loc[i][1]
            if (i == 0):
                beforePrice = None
                previousPeakPrice = currentPrice
                optimumPrice = currentPrice
            else:
                beforePrice = dailyEvaluationValance_df.loc[i - 1][1]

                if (beforePrice == currentPrice):
                    pass
                elif (beforePrice < currentPrice and previousPeakPrice < currentPrice):
                    tempMdd = round(float((optimumPrice - previousPeakPrice) / previousPeakPrice) * 100,
                                    2)  # 소수 둘째점에서 반올림함.
                    if (mdd > tempMdd):
                        mdd = tempMdd
                        previousPeakPrice = currentPrice
                        optimumPrice = currentPrice
                elif (beforePrice > currentPrice):
                    optimumPrice = currentPrice
                if (i == len(dailyEvaluationValance_df) - 1):  # 신고점이 달성되는 시점에만 연산되는 것 때문에 놓칠 수 있는 구간에 대한 mdd도 계산
                    tempMdd = round(float((optimumPrice - previousPeakPrice) / previousPeakPrice) * 100, 2)
                    if (mdd > tempMdd):
                        mdd = tempMdd

        print("mdd : " + str(mdd) + "%")

        # 하루 최악의 수익률
        print("bestBenefitAtDay : " + str(bestBenefitAtDay) + "%")

        # 하루 최상의 수익률
        print("worstBenefitAtDay : " + str(worstBenefitAtDay) + "%")

        # 총수익률
        totalBenefit = round(float((evaluation_balance - initial_money) / initial_money) * 100, 2)
        print("initial_money : " + str(initial_money))
        print("final_money : " + str(evaluation_balance))
        print("totalBenefit : " + str(totalBenefit) + "%")

        # 계산결과 Json변환
        date_list = []
        evaluation_money_list = []
        for i in range(0, len(dailyEvaluationValance_df)):
            date_list.append(dailyEvaluationValance_df.loc[i][0])
            evaluation_money_list.append(dailyEvaluationValance_df.loc[i][1])
        data = {}
        data["date"] = date_list
        data["evaluation_money"] = evaluation_money_list
        data["initial_money"] = str(initial_money)
        data["final_money"] = str(evaluation_balance)
        data["final_benefit"] = str(totalBenefit)
        data["mdd"] = str(mdd)
        data["best_benefit_day"] = str(bestBenefitAtDay)
        data["worst_benefit_day"] = str(worstBenefitAtDay)
        json_data = json.dumps(data, ensure_ascii=False)
        print(json_data)

    except Exception as e:
        print("error")
        print(e)

    return render(request, 'product_chartdata_graph.html', {'json_data': json_data})

def chartdata_item(request):
    startenddate = request.GET["startenddate"]
    print(startenddate)
    forStartDate = startenddate.replace(' ', '').split('-')[0].split('/')
    forEndDate = startenddate.replace(' ', '').split('-')[1].split('/')
    startDate = forStartDate[2] + forStartDate[0] + forStartDate[1]
    endDate = forEndDate[2] + forEndDate[0] + forEndDate[1]

    itemCode = request.GET["code"]
    print(itemCode)
    print(startDate)
    print(endDate)
    #startDate = "20160101"
    #endDate = "20160301"
    #itemCode = "000020"

    try:
        # DB연결
        engine = create_engine(
            'postgresql://postgres@localhost:9003/stockdb')  # 'postgresql://'+'POSTGRESQL_USER'+'POSTGRESQL_PASSWORD'+'POSTGRESQL_HOST_IP'+'POSTGRESQL_PORT'+'POSTGRESQL_DATABASE'

        item_df = read_sql(
            "SELECT date, close FROM stock_kospi.daily_price where code = \'" + itemCode + "\' and date >= \'" + startDate + "\' and date <= \'" + endDate + "\'" + " order by date",
            engine)

        # Json변환
        date_list = []
        price_list = []
        for i in range(0, len(item_df)):
            date_list.append(str(item_df.loc[i][0]))
            price_list.append(str(item_df.loc[i][1]))

        data = {}
        data["date"] = date_list
        data["evaluation_money"] = price_list
        data["headername"] = request.GET["headername"]
        json_data = json.dumps(data, ensure_ascii=False)
        print(json_data)

    except Exception as e:
        print("error")
        print(e)

    return render(request, 'product_chartdata_item.html', {'json_data': json_data})