#!/opt/anaconda3/envs/myenv/bin/python
import pandas as pd
from enum import IntEnum

class index(IntEnum):
    COMPTYPE = 0
    K1 = 1
    K2 = 2
    K3 = 3
    FBMCS = 4
    QMIN = 4
    FBMSS = 5
    QMAX = 5
    FBMNI = 6
    PMAX = 6
    WMIN = 7
    C1 = 7
    WMAX = 8
    C2 = 8
    C3 = 9
    FBM = 10
    
    NameIdx = 0
    EquipmentCostIdx = 1
    InstalledCostIdx = 2
    EquipmentWeightIdx = 3
    InstalledWeightIdx = 4
    UtilityCostIdx = 5
    HeatTransferAreaIdx = 6
    DriverPowerIdx = 7
    

def checkType(name):
    length = len(name)
    HTXLen = 3
    HEXLen = 3
    MIXLen = 3
    COMPLen = 4
    REACTLen = 5
    FLASHLen = 5
    
    for i in range(0, length):
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
        
data = []

pd.set_option("display.max_rows", None)       # 모든 행 보이기
pd.set_option("display.max_columns", None)    # 모든 열 보이기
pd.set_option("display.width", None)          # 줄바꿈 없이 가로로 다 보여주기
pd.set_option("display.max_colwidth", None)   # 열 안 문자열도 끝까지 다 보여주기
 
df = pd.read_excel(io = '../input/NH3.xlsx', sheet_name='Unit operation', usecols='C:H', header=3, engine='openpyxl')
for i in range(0, len(df), 1): #C랑 C++에 익숙해 2차원 딕셔너리를 생각을 못 했다 이게 더 간단할듯
    temp = [0 for K in range(8)]
    temp[index.NameIdx] = df.iat[i, index.NameIdx]
    temp[index.EquipmentCostIdx] = float(df.iat[i, index.EquipmentCostIdx]) # type 확인해서 <class 'numpy.int64'>면 int로, <class 'numpy.float64'>면 float으로 형변환하면 더 좋다.
    temp[index.InstalledCostIdx] = float(df.iat[i, index.InstalledCostIdx])
    temp[index.EquipmentWeightIdx] = float(df.iat[i, index.EquipmentWeightIdx])
    temp[index.InstalledWeightIdx] = float(df.iat[i, index.InstalledWeightIdx])
    temp[index.UtilityCostIdx] = float(df.iat[i, index.UtilityCostIdx])
    temp[index.HeatTransferAreaIdx] = 0.0
    temp[index.DriverPowerIdx] = 0.0
    data.append(temp)

# 이제 REACT, HTX, HEX, COMP. FLASH, MIX 이렇게 종류별로 저장해둬야함 -> Flash와 Mix의 비용은 없다치는건가?
# 이름 + 다섯 종류의 가격을 나타내야함. -> 2차원 배열로 저장하자(파이썬의 배열은 자료형이 전부 달라도 한 배열에 저장 가능하다
# Name, EquipmentCost, InstalledCost, EquipmentWeight, InstalledWeight, UtilityCost 순서로 저장하고, 배열의 인덱스를 저 이름으로 접근가능하게 enum 설정해서 가독성 높이자
# 2차원 배열 하나로만 저장하는걸로 -> type을 확인하는 함수만 하나 따로 만들어두자.

# TEMA HEX 시트의 각 Heat exchanger별 Heat transfer area [sqm]를 저장해둬야한다.
df = pd.read_excel(io = '../input/NH3.xlsx', sheet_name='TEMA HEX', usecols='C:K', header=1, engine='openpyxl')
for i in range(0, 8):
    name = df.iat[1, i]
    area = df.iat[8, i]
    for j in range(0, len(data)):
        if (data[j][index.NameIdx] == name):
            if (area != "nan"):
                data[j][index.HeatTransferAreaIdx] = float(area)
            break

# compressor의 power도 알아둬야함.
df = pd.read_excel(io = '../input/NH3.xlsx', sheet_name='Centrif gas compr', usecols='D:H', header=1, engine='openpyxl')
for i in range(0, 5):
	name = df.iat[1, i]
	power = df.iat[14, i]
	for j in range(0, len(data)):
		if (data[j][index.NameIdx] == name):
			if (area != "nan"):
				data[j][index.DriverPowerIdx] = float(power)
			break

HeatExchangerParam = {}
# HTX는 HEATER으로 Costdata sheet에서 Fired Heater Data의 Thermal Fluid Heaters 의 파라미터들을 사용해야함
HeatExchangerParam["HTX"] = {}

# HEX는 HEAT EXCHANGER으로 Heat Exchanger Data에서 Fixed tube, Floating Head, Bayonet의 파라미터들을 사용해야함
HeatExchangerParam["HEX"] = {}

# COMP는 COMPRESSOR로 Compressor Data (without electric motors)의 Centrifugal(근데 값이 세 개가 같아서 뭐인지 모름),Rotary의 파라미터들을 사용해야함.
HeatExchangerParam["COMP"] = {}

# Reactor의 입력 방식은 다시 생각해보자.
 
# U-Tube는 어디서 자료 가져온건지 나와있지 않음... 뭐지
df = pd.read_excel(io = '../input/NH3_TEA.xlsx', sheet_name='Centrif gas compr', usecols='D:H', header=1, engine='openpyxl')


print(data)