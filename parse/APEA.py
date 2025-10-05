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
HeatExchangerParam["COMP"] = {"K1": 2.2891, "K2": 1.3604, "K3": -0.1027}
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
		print("NAME : %-10s CONSUMPTION : %f" %(name, cost))
  
 
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
		temp["EQUIPMENT COST"] = (10**(temp["K1"] + temp["K2"] * (math.log(data[i][index.DriverPowerIdx], 10)) + (temp["K3"] * ((math.log(data[i][index.DriverPowerIdx], 10))**2)))) * (798.8 / 397)
		print(temp)
	# 여기는 이미 가격 계산 되어있으면 계산 안 하는 부분
	# if (data[i][index.EquipmentCostIdx] != 0): 
	# 	print(data[i][index.EquipmentCostIdx])
	# 	temp["EQUIPMENT COST"] = data[i][index.EquipmentCostIdx]
	# print(temp)
	cost[data[i][index.NameIdx]] = deepcopy(temp)
	 
# print(cost)
# 이제 여기서 Capacity 값은 각 모듈별로 파싱해서 저장해둬야함.

'''
	이제 Utility값 파싱해서 저장하는 부분
	장치별로 COOLING UTILITY, HOT UTILITY, ELECTRICITY UTILITY를 저장해야한다.
	COOLING UTILITY는 UTILITY USAGE [kg/hr], ANNUAL USAGE [kg/year], UTILITY COST [USD/hr], ANNUAL COST [USD/year]로 이루어져 있고
	HOT UTILITY는 DUTY [kW], ANNUAL DUTY [kWh/year], REQUIRED Utility [kg/hr], ANNUAL COST [USD/year]로 이루어져 있고, 
	ELECTRICITY UTILITY는 UTILITY USAGE [kW], ANNUAL USAGE [kWh/year], ANNUAL COST [USD/year]로 이루어져 있다.
	기계 종류별로 정해져 있는 utility가 아니라 각 기계에서 어떤 일을 하는지에 따라 어떤 유틸리티를 저장하는지 달라진다.
'''

''' 
	Aspen에는             
 				 UTILITY SECTION........................................ 37
                 UTILITY USAGE:  COOLINGW  (WATER)................. 37
                 UTILITY USAGE:  ELECTRO   (ELECTRICITY)........... 38
                 UTILITY USAGE:  FIRE1000  (GENERAL)............... 39
                 UTILITY USAGE:  HOTOIL    (GENERAL)............... 40
    다음과같이 섹션이 나눠져 있다.
    
    BLOCK:  H-COMP-1 MODEL: COMPR (CONTINUED)  에
    UTILITY ID FOR ELECTRICITY               ELECTRO
  	RATE OF CONSUMPTION                    4153.8584  KW              
  	COST                                    321.9240  $/HR            
  	CO2 EQUIVALENT EMISSIONS               1296.6054  KG/HR  와 같이 나와있다.
   
   여기서 COMSUMPTION과 COST를 활용하여 원하는 utility값을 뽑아내면 완료
   
   1. COOLING의 Water 사용량은 COOLINGW 검색해서 아래에 나오는 사용량 뽑아내면 됨
     UTILITY ID FOR WATER                    COOLINGW
  	 RATE OF CONSUMPTION                    3.7253+05  KG/HR  
    
   2. HEATING의 DUTY 사용량은 HEAT DUTY  CAL/SEC  0.32239E+06
   	  에서 해당 CAL을 4.184 J을 활용하여 변환하고 KW 단위로 변경하면 된다.
                                 ***  RESULTS  ***
   	OUTLET TEMPERATURE    C                                    420.00    
   	OUTLET PRESSURE       BAR                                  274.00    
   	HEAT DUTY             CAL/SEC                             0.32239E+06
   	OUTLET VAPOR FRACTION                                      1.0000   
   
   3. ELECTRICITY는  UTILITY ID FOR ELECTRICITY 에서 다음 줄인
   	  RATE OF CONSUMPTION  의 값을 읽어오면 된다.
      
      UTILITY ID FOR ELECTRICITY               ELECTRO
  	  RATE OF CONSUMPTION                    4153.8584  KW 
    
    ** HEX의 유틸리티값은 파일에서도 제외되어 있어서 일단 뺌
    ** COOLER는 HEAT DUTY + WATER CONSUMPTION 둘 다 있어서 COOLING있는 애면 DUTY 파싱하지 않기
    -> 이제 이걸로 Utility값 읽어와서 파일에 출력하면 끝
'''

fd = open("./input/nh3_demo.rep", mode='r')
lines = fd.readlines()
parseflag = 1
utility =  {}
for line in lines:
	if ("BLOCK:" in line):
		temp = list(line.split("  "))
		temp2 = temp[1].split(": ")
		temp2 = temp2[0].split(" ")
		name = temp2[0]
		if (checkType(name) == "HEX"):
			parseflag = 0
		else:
			parseflag = 1
	if ("COOLING" in line):
		parseflag = 2
	if ("ELECTRO" in line):
		parseflag = 3
  
	if ((parseflag == 2 or parseflag == 3)and "RATE OF CONSUMPTION" in line):
		temp = list(line.split("                    "))
		temp2 = list(temp[1].split(" "))
		temp3 = list(temp2[0].split('+'))
		num = float(temp3[0])
		if (len(temp3) > 1):
			for i in range(int(temp3[1])):
				num *=  10
		print("NAME : %-10s CONSUMPTION : %s" %(name, num))
		if (parseflag == 2):
			utility[name] = ["COOLING UTILITY", num]
		if (parseflag == 3):
			utility[name] = ["ELECTRICITY UTILITY", num]
  
	if (parseflag == 1 and "HEAT DUTY" in line):
		temp = list(line.split("CAL/SEC"))
		for i in range(0, len(temp)):
			temp[i] = temp[i].replace(" ", "").replace('\n', "").replace('E', "")
		if (len(temp) > 1):
			temp3 = list(temp[1].split('+'))
			num = float(temp3[0])
			if (len(temp3) > 1):
				for i in range(int(temp3[1])):
					num *=  10
		else:
			num = temp[0]
		# num 단위변환
		num *= 0.004184
		print("NAME : %-10s HEAT DUTY : %s" %(name, num))
		utility[name] = ["HOT UTILITY", num]

#이제 예쁘게 출력만 하면 완성이다~

parse_out = pd.DataFrame(data)
parse_out.columns = ["Name", "EquipmentCost", "InstalledCost", "EquipmentWeight", "InstalledWeight", "UtilityCost", "HeatTransferArea", "DriverPower"]
# parse_out = pd.DataFrame(data)
capcost = pd.DataFrame(cost)
utility_cost = pd.DataFrame(utility)

# Excel로 저장
with pd.ExcelWriter("output.xlsx", mode="w", engine="openpyxl") as writer:
	parse_out.to_excel(writer, sheet_name="parse", index=False) # 행번호 빼고 저장하겠다.
	capcost.to_excel(writer, sheet_name="CAPCOST")
	utility_cost.to_excel(writer, sheet_name="UTILITY")
	
# U-Tube는 어디서 자료 가져온건지 나와있지 않음... 뭐지
# df = pd.read_excel(io = '../input/NH3_TEA.xlsx', sheet_name='Centrif gas compr', usecols='D:H', header=1, engine='openpyxl')


# print(data)