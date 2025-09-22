#!/opt/anaconda3/envs/myenv/bin/python
import pandas as pd
from enum import IntEnum

def checkType(name):
    length = len(name)
    HTXLen = 3
    HEXLen = 3
    MIXLen = 3
    COMPLen = 4
    REACTLen = 5
    FLASHLen = 5
    
    for i in range(0, length):
        # print(name[i:i + HTXLen], i)
        if (length - i + 1 >= HTXLen and name[i:i + HTXLen] == "HTX"):
            return "HTX"
        elif (length - i + 1 >= HEXLen and name[i:i + HEXLen] == "HEX"):
            return "HEX"
        elif (length - i + 1 >= MIXLen and name[i:i + MIXLen] == "MIX"):
            return "MIX"
        elif (length - i + 1 >= COMPLen and name[i:i + COMPLen] == "COMP"):
            return "COMP"
        elif (length - i + 1 >= REACTLen and name[i:i + REACTLen] == "REACT"):
            return "REACT"
        elif (length - i + 1 >= FLASHLen and name[i:i + FLASHLen] == "FLASH"):
            return "FLASH"
        
class index(IntEnum):
    NameIdx = 0
    EquipmentCostIdx = 1
    InstalledCostIdx = 2
    EquipmentWeightIdx = 3
    InstalledWeightIdx = 4
    UtilityCostIdx = 5

data = []
EquipmentCost = []
InstalledCost = []
EquipmentWeight = []
InstalledWeight = []
UtilityCost = []

pd.set_option("display.max_rows", None)       # 모든 행 보이기
pd.set_option("display.max_columns", None)    # 모든 열 보이기
pd.set_option("display.width", None)          # 줄바꿈 없이 가로로 다 보여주기
pd.set_option("display.max_colwidth", None)   # 열 안 문자열도 끝까지 다 보여주기
 
df = pd.read_excel(io = '../input/NH3.xlsx', sheet_name='Unit operation', usecols='C:H', header=3, engine='openpyxl')
for i in range(0, len(df), 1):
    temp = []
    temp.append(df.iat[i, index.NameIdx])
    temp.append(float(df.iat[i, index.EquipmentCostIdx])) # type 확인해서 <class 'numpy.int64'>면 int로, <class 'numpy.float64'>면 float으로 형변환하면 더 좋다.
    temp.append(float(df.iat[i, index.InstalledCostIdx]))
    temp.append(float(df.iat[i, index.EquipmentWeightIdx]))
    temp.append(float(df.iat[i, index.InstalledWeightIdx]))
    temp.append(float(df.iat[i, index.UtilityCostIdx]))
    data.append(temp)
    print(checkType(data[i][index.NameIdx]))

print(data)
# 이제 REACT, HTX, HEX, COMP. FLASH, MIX 이렇게 종류별로 저장해둬야함
# 이름 + 다섯 종류의 가격을 나타내야함. -> 2차원 배열로 저장하자(파이썬의 배열은 자료형이 전부 달라도 한 배열에 저장 가능하다
# Name, EquipmentCost, InstalledCost, EquipmentWeight, InstalledWeight, UtilityCost 순서로 저장하고, 배열의 인덱스를 저 이름으로 접근가능하게 enum 설정해서 가독성 높이자
# 2차원 배열 하나로만 저장하는걸로 -> type을 확인하는 함수만 하나 따로 만들어두자.

