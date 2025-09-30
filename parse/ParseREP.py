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
			for i in range(int(temp3[1])):
				cost *=  10
		print("NAME : %-10s CONSUMPTION : %s" %(name, cost))
  