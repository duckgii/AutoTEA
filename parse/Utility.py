import math
from copy import deepcopy
from enums import Index
import pandas as pd

### 파라미터 값 초기화 부분 ###

HeatExchangerParam = {}
# HTX는 HEATER으로 Costdata sheet에서 Fired Heater Data의 Thermal Fluid Heaters 의 파라미터들을 사용해야함
HeatExchangerParam["HTX"] = {"K1": 2.2628, "K2": 0.8581, "K3": 0.0003, "B1":1.63, "B2":1.66, "FM":1.35} 
#Diphenyl heater 방식으로 우선 계산.
#K값은 "Fired Heater Data"에서, B값은 "Heat Exchanger Data"에서,Fm값은 "Material Factors, FM" 여기서 가져왔다.

# HEX는 HEAT EXCHANGER으로 Heat Exchanger Data에서 Fixed tube, Floating Head, Bayonet의 파라미터들을 사용해야함
HeatExchangerParam["HEX"] = {"K1": 4.3247, "K2": -0.303, "K3": 0.1634, "B1":1.63, "B2":1.66, "FM":1.35}
# Fixed tube 방식으로 우선 계산

# COMP는 COMPRESSOR로 Compressor Data (without electric motors)의 Centrifugal(근데 값이 세 개가 같아서 뭐인지 모름),Rotary의 파라미터들을 사용해야함.
HeatExchangerParam["COMP"] = {"K1": 2.2891, "K2": 1.3604, "K3": -0.1027}
# Centrifugal, axial and reciprocating 방식으로 우선 계산.
# Reactor의 입력 방식은 다시 생각해보자.

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

# cost = {} # 2차원 딕셔너리로 "이름" : {딕셔너리} 이렇게 저장하고 각 유닛 종류별 인자와 계산 결과를 출력한다.
def calCAPCOST(inputData, cost):
	for i in range(0, len(inputData), 1):
		temp = {}
		type = checkType(inputData[i][Index.NameIdx])

 		# 여기서 이제 cost의 값들을 하나씩 이름, 인자 순으로 저장해야함.
		'''
		1. EQUIPMENT COST
		- HEX, HTX : ((10^(K1+K2+K3))*(Capacity / 10)^(0.6)) * (CEPCI(June 2024) / CEPCI(Sept 2001))
		- COMP : (10^(K1 + K2 * log(Capacity) + K3 * ((log(Capacity))^2))) * (CEPCI(June 2024) / CEPCI(Sept 2001))
		2. C_BM 
		- HEX, HTX : EQUIPMENT COST * (B1 + B2*FM)
		'''
		if (type == "HEX"):
			temp = deepcopy(HeatExchangerParam["HEX"])
			temp["EQUIPMENT COST"] = ((10**(temp["K1"]+temp["K2"]+temp["K3"]))*(inputData[i][Index.HeatTransferAreaIdx] / 10)**(0.6)) * (798.8 / 397)
			temp["C_BM"] = temp["EQUIPMENT COST"] * (temp["B1"] + temp["B2"] * temp["FM"])
		elif (type == "HTX"):
			temp = deepcopy(HeatExchangerParam["HTX"])
			temp["EQUIPMENT COST"] = ((10**(temp["K1"]+temp["K2"]+temp["K3"]))*(inputData[i][Index.HeatTransferAreaIdx] / 10)**(0.6)) * (798.8 / 397)
			temp["C_BM"] = temp["EQUIPMENT COST"] * (temp["B1"] + temp["B2"] * temp["FM"])
		elif (type == "COMP"):
			temp = deepcopy(HeatExchangerParam["COMP"])
			temp["EQUIPMENT COST"] = (10**(temp["K1"] + temp["K2"] * (math.log(inputData[i][Index.DriverPowerIdx], 10)) + (temp["K3"] * ((math.log(inputData[i][Index.DriverPowerIdx], 10))**2)))) * (798.8 / 397)
			print(temp)
		# 여기는 이미 가격 계산 되어있으면 계산 안 하는 부분
		# if (inputData[i][Index.EquipmentCostIdx] != 0): 
		# 	print(inputData[i][Index.EquipmentCostIdx])
		# 	temp["EQUIPMENT COST"] = inputData[i][Index.EquipmentCostIdx]
		# print(temp)
		cost[inputData[i][Index.NameIdx]] = deepcopy(temp)
	 
# print(cost)
# 이제 여기서 Capacity 값은 각 모듈별로 파싱해서 저장해둬야함.
def safe_df(df):
    # 인덱스가 RangeIndex(0,1,2,...)가 아니거나, 인덱스 이름이 있다면 컬럼으로 복구
    if not isinstance(df.index, pd.RangeIndex) or df.index.name is not None:
        return df.reset_index()
    return df

def printout(inputData, cost, utility):
	parse_out = pd.DataFrame(inputData)
	parse_out.columns = ["Name", "EquipmentCost", "InstalledCost", "EquipmentWeight", "InstalledWeight", "UtilityCost", "HeatTransferArea", "DriverPower"]
	capcost = pd.DataFrame(cost)
	utility_cost = pd.DataFrame(utility)

	with pd.ExcelWriter("output.xlsx", engine="xlsxwriter") as writer:
		parse_out2   = safe_df(parse_out)
		capcost2     = safe_df(capcost)
		utility2     = safe_df(utility_cost)

		parse_out2.to_excel(writer, sheet_name="parse",   index=False)
		capcost2.to_excel(writer,   sheet_name="CAPCOST", index=False)
		utility2.to_excel(writer,   sheet_name="UTILITY", index=False)

	    # (옵션) 자동 너비 맞추기
		for name, df in [("parse", parse_out2), ("CAPCOST", capcost2), ("UTILITY", utility2)]:
			ws = writer.sheets[name]
			for c, col in enumerate(df.columns):
				maxlen = max(len(str(col)), *(len(str(v)) for v in df[col].astype(str)))
				ws.set_column(c, c, min(maxlen + 2, 60))
            
# U-Tube는 어디서 자료 가져온건지 나와있지 않음... 뭐지
# df = pd.read_excel(io = '../input/NH3_TEA.xlsx', sheet_name='Centrif gas compr', usecols='D:H', header=1, engine='openpyxl')


# print(inputData)
