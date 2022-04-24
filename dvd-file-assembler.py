import os, shutil, time

dataFolder = ".\\example\\data\\"	# folder where data is stored and must be splitted on multiple dvds
par2Folder = ".\\example\\par2\\"	# folder where par2 data is stored and must be splitted on multiple dvds
duplFolder = ".\\example\\dupl\\"	# folder where data must be present on all dvds
outFolder  = ".\\out\\"

dvdSize = 500000000

class statusBar():
	def __init__(self, lenght, p1=0, p2=0):
		self.lenght = lenght
		self.bar = ""
		self.p1 = p1
		self.p2 = p2
	
	def show(self):
		self.bar = ""
		self.bar += "#" * int(self.lenght * self.p2/self.p1)
		self.bar += "-" * int(self.lenght * (self.p1-self.p2)/self.p1)
		print("\r" + self.bar, end="")
	
	def addp1(self):
		self.p1 += 1
	def addp2(self):
		self.p2 += 1

class DVD():
	def __init__(self, id, dataSizeReserved, par2SizeReserved, duplSizeReserved):
		self.usableSizeData = dataSizeReserved
		self.usableSizePar2 = par2SizeReserved
		self.usableSizeDupl = duplSizeReserved
		self.id = id
		self.folder = os.path.join(outFolder, "dvd" + str(self.id))
		self.dic = {}
		self.statusBar = statusBar(84)

		os.path.exists(outFolder) or os.makedirs(outFolder, exist_ok=True)
		os.path.exists(self.folder) or os.makedirs(self.folder, exist_ok=True)
		print(("DVD"+str(self.id)+" reserved:").ljust(16, " "),
				(str(self.usableSizeData)+" data").rjust(16, " "),
				(str(self.usableSizePar2)+" par2").rjust(16, " "),
				(str(self.usableSizeDupl)+" dupl").rjust(16, " "),
				(str(dvdSize) + " dvd").rjust(16, " "),
			)
	
	def addData(self, file):
		fsize = os.path.getsize(file)
		if self.usableSizeData < fsize:
			return "file too big"
		self.dic[file] = os.path.join(self.folder, file.replace(dataFolder, ""))
		self.usableSizeData -= fsize
		self.statusBar.addp1()
		return None

	def addPar2(self, file):
		fsize = os.path.getsize(file)
		if self.usableSizePar2 < fsize:
			return "file too big"
		self.dic[file] = os.path.join(self.folder, file.replace(par2Folder, "_par2\\"))
		self.usableSizePar2 -= fsize
		self.statusBar.addp1()
		return None
	
	def addDupl(self, file):
		fsize = os.path.getsize(file)
		self.dic[file] = os.path.join(self.folder, file.replace(duplFolder, "_dupl\\"))
		self.usableSizeDupl -= fsize
		self.statusBar.addp1()
		return None
	
	def save(self):
		for ori in self.dic:
			des = self.dic[ori]
			if os.path.isdir(ori):
				os.path.exists(des) or os.makedirs(des, exist_ok=True)
			if os.path.isfile(ori):
				os.path.exists(os.path.dirname(des)) or os.makedirs(os.path.dirname(des), exist_ok=True)
				shutil.copy2(ori, des)
			self.statusBar.addp2()
			self.statusBar.show()
		
		self.writtenSize = SizeFolder(self.folder)
		self.writtenSizePar2 = SizeFolder(os.path.join(self.folder, "_par2\\"))
		self.writtenSizeDupl = SizeFolder(os.path.join(self.folder, "_dupl\\"))
		self.writtenSizeData = self.writtenSize - self.writtenSizePar2 - self.writtenSizeDupl
		self.warning = ""
		if self.writtenSize > 0.95 * dvdSize:
			self.warning = "DVD"+str(self.id)+" is near/exceding dvd size limit"
		
		print()
		print("written fold:".ljust(16, " "),
				(str(self.writtenSizeData)+" data").rjust(16, " "),
				(str(self.writtenSizePar2)+" par2").rjust(16, " "),
				(str(self.writtenSizeDupl)+" dupl").rjust(16, " "),
				(str(self.writtenSize)+" dvd").rjust(16, " "),
				self.warning
			)
		print("% of dvd:".ljust(16, " "),
				(str(int(10000*self.writtenSizeData/dvdSize)/100)+" % data").rjust(16, " "),
				(str(int(10000*self.writtenSizePar2/dvdSize)/100)+" % par2").rjust(16, " "),
				(str(int(10000*self.writtenSizeDupl/dvdSize)/100)+" % dupl").rjust(16, " "),
				(str(int(10000*(self.writtenSize)/dvdSize)/100) + " % dvd").rjust(16, " ")
			)
		print()

		return self.warning

def main():
	maxFill = 0.9				# maxFill indicates how much the dvd can be filled with storage
	availablePhysicalDvd = 15	# availablePhysicalDvd is the number of available blank dvds for the backup

	if os.path.exists(outFolder):
		shutil.rmtree(outFolder)

	dataFiles = getFileList(dataFolder)
	par2Files = getFileList(par2Folder)
	duplFiles = getFileList(duplFolder)

	dataFilesSize = SizeList(dataFiles)
	par2FilesSize = SizeList(par2Files)
	duplFilesSize = SizeList(duplFiles)

	# !!! fix wrong calc of storageFiles: should count that duplFilesSize is greater with multiple dvds
	storageFiles = (dataFilesSize+par2FilesSize+duplFilesSize)
	# !!! fix wrong calc of dvdRemaining: says 15 will be created but it creates 16
	dvdRemaining = int(-((storageFiles) // -(maxFill * dvdSize)))	# estimate needed dvd (ceiling the value)
	storageXdvd = int(1.02 * storageFiles/dvdRemaining)				# make it a big bigger to leave some space for play
	par2FilesSizeMax = int((availablePhysicalDvd*maxFill*dvdSize) - dataFilesSize - duplFilesSize) # current max par2 folder size with current config

	print("".ljust(50, "-"))
	print("total storage:".ljust(22, " "),		str(storageFiles).rjust(12, " "),	"use of", dvdRemaining, "dvds at", str(maxFill*100) + "% maxfill")
	print("max storage on dvd:".ljust(22, " "),	str(storageXdvd).rjust(12, " "),	"("+str(int(10000*storageXdvd/dvdSize)/100)+"%) of dvd")
	
	print("par2 size now:".ljust(22, " "),		str(par2FilesSize).rjust(12, " "))
	print("par2 size can reach:".ljust(22, " "),str(par2FilesSizeMax).rjust(12, " "),	"to use", availablePhysicalDvd, "dvds at", str(maxFill*100) + "% maxfill")
	print("".ljust(50, "-"))
	
	if input("continue? (y/N)") != "y":
		exit()

	n = -1
	warnings = []
	while len(dataFiles) > 0 or len(par2Files) > 0:
		n += 1

		dataFilesSize = SizeList(dataFiles)
		par2FilesSize = SizeList(par2Files)
		duplFilesSize = SizeList(duplFiles)
		
		# !!! fix wrong calc of storageFiles: should count that duplFilesSize is greater with multiple dvds
		storageFiles = (dataFilesSize+par2FilesSize+duplFilesSize)
		dvdRemaining = int(-((storageFiles) // -(maxFill * dvdSize))) # estimate needed dvd (ceiling the value)
		storageXdvd = int(1.02 * storageFiles/dvdRemaining) # make it a big bigger to leave some space for play
		print(dvdRemaining, "dvds to be created")
		
		dvd = DVD(n,
					int(storageXdvd * dataFilesSize/storageFiles),
					int(storageXdvd * par2FilesSize/storageFiles),
					duplFilesSize)

		for f in duplFiles:
			dvd.addDupl(f)
	
		for f in dataFiles[:]: # iterate over copy of list
			err = dvd.addData(f)
			if err != None:
				break
			dataFiles.remove(f)
		
		for f in par2Files[:]: # iterate over copy of list
			err = dvd.addPar2(f)
			if err != None:
				break
			par2Files.remove(f)
		
		warn = dvd.save()
		if warn != "":
			warnings.append(warn)
	
	if warnings != []:
		print("one or more DVD reported warnings:\n" + "\n".join(warnings))

def getFileList(folder):
	files = []
	for (root, dirs, file) in os.walk(folder):
		files.append(os.path.join(root, "")) # add root folder (in case the folder is empty)
		for f in file:
			files.append(os.path.join(root, f))
	files.sort()
	return files

def SizeFolder(Folderpath, exclude=[]):
	size = 0
	for path, dirs, files in os.walk(Folderpath):
		for f in files:
			# skip files in exclude list
			fp = os.path.join(path, f)
			if any(e in fp for e in exclude):
				continue
			size += os.path.getsize(fp)
	return size

def SizeList(FileList):
	size = 0
	for f in FileList:
		size += os.path.getsize(f)
	return size

if __name__ == "__main__":
	main()