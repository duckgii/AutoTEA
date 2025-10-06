from enum import IntEnum


class Index(IntEnum):
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
