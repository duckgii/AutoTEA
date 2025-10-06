#!/opt/anaconda3/envs/myenv/bin/python
from Parse import parseTEA, parseHEX, parseCOMP, parseCAPCOSTParam, parseUtility
from Utility import calCAPCOST, printout

inputData = []
inputfile = "./input/NH3.xlsx"
inputrep = "./input/NH3_demo.rep"
parseTEA(inputfile, inputData)
parseHEX(inputfile, inputData)
parseCOMP(inputfile, inputData)
parseCAPCOSTParam(inputrep, inputData)
  
cost = {} # 2차원 딕셔너리로 "이름" : {딕셔너리} 이렇게 저장하고 각 유닛 종류별 인자와 계산 결과를 출력한다.
calCAPCOST(inputData, cost)

# 이제 여기서 Capacity 값은 각 모듈별로 파싱해서 저장해둬야함.
utility =  {}
parseUtility(inputrep, utility)
#이제 예쁘게 출력만 하면 완성이다~

printout(inputData, cost, utility)
