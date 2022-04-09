import os

dataFolder = ".\\example\\data\\"		# folder where data is stored and must be splitted on multiple dvds
par2Folder = ".\\example\\par2\\"		# folder where par2 data is stored and must be splitted on multiple dvds
duplFolder  = ".\\example\\duplicate\\"	# folder where data must be present on all dvds

dvdDimension = 100000000

def main():	
	for (root, dirs, file) in os.walk(dataFolder):
		print(root)
		print(dirs)
		print(file, end="\n\n")

if __name__ == "__main__":
	main()