#!/opt/anaconda3/envs/myenv/bin/python
import pandas as pd
from enum import IntEnum
import math
from copy import deepcopy

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
 
df = pd.read_excel(io = './input/NH3.xlsx', sheet_name='Unit operation', usecols='C:H', header=3, engine='openpyxl')
for i in range(0, len(df), 1): #C랑 C++에 익숙해 2차원 딕셔너리를 생각을 못 했다 이게 더 간단할듯 근데 그거나 그거나 비슷함
	temp = [0 for K in range(8)]
	temp[index.NameIdx] = df.iat[i, index.NameIdx]
	temp[index.EquipmentCostIdx] = float(df.iat[i, index.EquipmentCostIdx]) # type 확인해서 <class 'numpy.int64'>면 int로, <class 'numpy.float64'>면 float으로 형변환하면 더 좋다.
	temp[index.InstalledCostIdx] = float(df.iat[i, index.InstalledCostIdx])
	temp[index.EquipmentWeightIdx] = float(df.iat[i, index.EquipmentWeightIdx])
	temp[index.InstalledWeightIdx] = float(df.iat[i, index.InstalledWeightIdx])
	temp[index.UtilityCostIdx] = float(df.iat[i, index.UtilityCostIdx])
	temp[index.HeatTransferAreaIdx] = 0.0 
	#-> 이거 없는 경우 파싱 다른 곳에서 해서 가져와야함 HTX는 "RATE OF CONSUMPTION"  이거 찾아서 가져오면 됨
	# HEX는 "ZONE HEAT TRANSFER AND AREA" 에서 AREA 값 가져오면 됨
	temp[index.DriverPowerIdx] = 0.0
	# 이거 없는 경우는 .rep에서 COMP의 "RATE OF CONSUMPTION" 이거 가져오면 됨. 근데 이 데이터 rep 말고 xml 있으면 더 편할 것 같음.
	data.append(temp)

# 이제 REACT, HTX, HEX, COMP. FLASH, MIX 이렇게 종류별로 저장해둬야함 -> Flash와 Mix의 비용은 없다치는건가?
# 이름 + 다섯 종류의 가격을 나타내야함. -> 2차원 배열로 저장하자(파이썬의 배열은 자료형이 전부 달라도 한 배열에 저장 가능하다
# Name, EquipmentCost, InstalledCost, EquipmentWeight, InstalledWeight, UtilityCost 순서로 저장하고, 배열의 인덱스를 저 이름으로 접근가능하게 enum 설정해서 가독성 높이자
# 2차원 배열 하나로만 저장하는걸로 -> type을 확인하는 함수만 하나 따로 만들어두자.

# TEMA HEX 시트의 각 Heat exchanger별 Heat transfer area [sqm]를 저장해둬야한다.
df = pd.read_excel(io = './input/NH3.xlsx', sheet_name='TEMA HEX', usecols='C:K', header=1, engine='openpyxl')
for i in range(0, 8):
	name = df.iat[1, i]
	area = df.iat[8, i]
	for j in range(0, len(data)):
		if (data[j][index.NameIdx] == name):
			if (area != "nan"):
				data[j][index.HeatTransferAreaIdx] = float(area) 
    			# HTX는 이 값으로 구하는 거 아니라서 변경해야함.Capacity (kW)를 활용함.. 또 쿨러는 뭔가 다른 것 같은데.. 우선 계산된 값은 건드리지 말자.
			break

# compressor의 power도 알아둬야함.
df = pd.read_excel(io = './input/NH3.xlsx', sheet_name='Centrif gas compr', usecols='D:H', header=1, engine='openpyxl')
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
HeatExchangerParam["HTX"] = {"K1": 2.2628, "K2": 0.8581, "K3": 0.0003, "B1":1.63, "B2":1.66, "FM":1.35} 
#Diphenyl heater 방식으로 우선 계산.
#K값은 "Fired Heater Data"에서, B값은 "Heat Exchanger Data"에서,Fm값은 "Materail Factors, FM" 여기서 가져왔다.

# HEX는 HEAT EXCHANGER으로 Heat Exchanger Data에서 Fixed tube, Floating Head, Bayonet의 파라미터들을 사용해야함
HeatExchangerParam["HEX"] = {"K1": 4.3247, "K2": -0.303, "K3": 0.1634, "B1":1.63, "B2":1.66, "FM":1.35}
# Fixed tube 방식으로 우선 계산

# COMP는 COMPRESSOR로 Compressor Data (without electric motors)의 Centrifugal(근데 값이 세 개가 같아서 뭐인지 모름),Rotary의 파라미터들을 사용해야함.
HeatExchangerParam["COMP"] = {"K1": 4.3247, "K2": -0.303, "K3": 0.1634}
# Centrifugal, axial and reciprocating 방식으로 우선 계산.
# Reactor의 입력 방식은 다시 생각해보자.

fd = open("./input/nh3_demo.rep", mode='r')
lines = fd.readlines()

for line in lines:
	if ("BLOCK:" in line):
		temp = list(line.split("  "))
		temp2 = temp[1].split(": ")
		temp2 = temp2[0].split(" ")
		name = temp2[0]
	if ("RATE OF CONSUMPTION" in line):
		temp = list(line.split("                    "))
		temp2 = list(temp[1].split(" "))
		temp3 = list(temp2[0].split('+'))
		cost = float(temp3[0])
		if (len(temp3) > 1):
			for i in range(0, int(temp3[1])):
				cost *=  10
		for i in range(0, len(data)):
			if (data[i][index.NameIdx] == name):
				if (checkType(name) == "HTX"):
					data[i][index.HeatTransferAreaIdx] = cost
				elif (checkType(name) == "COMP"):
					data[i][index.DriverPowerIdx] = cost
		# print("NAME : %-10s CONSUMPTION : %s" %(name, cost))
  
 
cost = {} # 2차원 딕셔너리로 "이름" : {딕셔너리} 이렇게 저장하고 각 유닛 종류별 인자와 계산 결과를 출력한다.
for i in range(0, len(data), 1):
	temp = {}
	type = checkType(data[i][index.NameIdx])
	
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
		temp["EQUIPMENT COST"] = ((10**(temp["K1"]+temp["K2"]+temp["K3"]))*(data[i][index.HeatTransferAreaIdx] / 10)**(0.6)) * (798.8 / 397)
		temp["C_BM"] = temp["EQUIPMENT COST"] * (temp["B1"] + temp["B2"] * temp["FM"])
	elif (type == "HTX"):
		temp = deepcopy(HeatExchangerParam["HTX"])
		temp["EQUIPMENT COST"] = ((10**(temp["K1"]+temp["K2"]+temp["K3"]))*(data[i][index.HeatTransferAreaIdx] / 10)**(0.6)) * (798.8 / 397)
		temp["C_BM"] = temp["EQUIPMENT COST"] * (temp["B1"] + temp["B2"] * temp["FM"])
	elif (type == "COMP"):
		temp = deepcopy(HeatExchangerParam["COMP"])
		temp["EQUIPMENT COST"] = (10**(temp["K1"] + temp["K2"] * math.log(data[i][index.DriverPowerIdx], 10) + temp["K3"] * ((math.log(data[i][index.DriverPowerIdx]))**2)))
	if (data[i][index.EquipmentCostIdx] != 0):
		# print(data[i][index.EquipmentCostIdx])
		temp["EQUIPMENT COST"] = data[i][index.EquipmentCostIdx]
	print(temp)
	cost[data[i][index.NameIdx]] = deepcopy(temp)
	 
print(cost)
# 이제 여기서 Capacity 값은 각 모듈별로 파싱해서 저장해둬야함.



parse_out = pd.DataFrame(data)
parse_out.columns = ["Name", "EquipmentCost", "InstalledCost", "EquipmentWeight", "InstalledWeight", "UtilityCost", "HeatTransferArea", "DriverPower"]
# parse_out = pd.DataFrame(data)
capcost = pd.DataFrame(cost)

# Excel로 저장
with pd.ExcelWriter("output.xlsx", mode="w", engine="openpyxl") as writer:
	parse_out.to_excel(writer, sheet_name="parse", index=False) # 행번호 빼고 저장하겠다.
	capcost.to_excel(writer, sheet_name="CAPCOST")
	
# U-Tube는 어디서 자료 가져온건지 나와있지 않음... 뭐지
# df = pd.read_excel(io = '../input/NH3_TEA.xlsx', sheet_name='Centrif gas compr', usecols='D:H', header=1, engine='openpyxl')


# print(data)