import os

dataToDvds = ".\exampledata"	# folder where data is stored and must be splitted on multiple dvds
par2ToDvds = ".\examplepar2"	# folder where par2 data is stored and must be splitted on multiple dvds
inAllDvds =   ".\inall"			# folder where data must be present on all dvds

dvdDimension = 100000000

def main():	
	for (root, dirs, file) in os.walk(dataToDvds):
		print(root)
		print(dirs)
		print(file, end="\n\n")

if __name__ == "__main__":
	main()