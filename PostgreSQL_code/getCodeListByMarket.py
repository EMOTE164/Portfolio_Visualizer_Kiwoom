#GetCodeListByMarket, GetMasterCodeName을 이용해 시장에 따른 전체 종목코드와 한글이름을 가져올 수 있음

import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import time

class Program(QMainWindow):

    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")  # 로그인창 호출
        # 서버로부터 오는 이벤트에 콜백함수 등록
        self.kiwoom.OnEventConnect.connect(self.receiveLoginEvent)

    # 로그인창에서 아이디와 패스워드가 맞으면 불리는 함수
    def receiveLoginEvent(self, err_code):
        if err_code == 0:
            print("로그인 성공")

            ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["0"]) #0: 코스피, 10: 코스닥, 3: ELW, 8: ETF, 50: 코넥스, 4: 뮤추얼펀드, 5: 신주인수권, 6: 리츠, 9: 하이얼펀드, 30: K-PTC
            kospi_code_list = ret.split(';')
            kospi_code_name_list = []

            for code in kospi_code_list:
                name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [code])
                kospi_code_name_list.append(code + " : " + name)

            print(kospi_code_name_list)
            print(len(kospi_code_name_list))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    trace = Program()
    app.exec_()