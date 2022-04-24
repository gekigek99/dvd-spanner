import os, shutil
import math

dataFolder = ".\\example\\data\\"	# folder where data is stored and must be splitted on multiple dvds
par2Folder = ".\\example\\par2\\"	# folder where par2 data is stored and must be splitted on multiple dvds
duplFolder = ".\\example\\dupl\\"	# folder where data must be present on all dvds
outFolder  = ".\\out\\"

dvdSize = 500000000

class DVD():
	def __init__(self, id, dataSizeReserved, par2SizeReserved, duplSizeReserved):
		self.usableSizeData = dataSizeReserved
		self.usableSizePar2 = par2SizeReserved
		self.usableSizeDupl = duplSizeReserved
		self.id = id
		self.folder = os.path.join(outFolder, "dvd" + str(self.id))
		self.fileDic = {}
		
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
		self.fileDic[file] = os.path.join(self.folder, file.replace(dataFolder, ""))
		self.usableSizeData -= fsize
		return None

	def addPar2(self, file):
		fsize = os.path.getsize(file)
		if self.usableSizePar2 < fsize:
			return "file too big"
		self.fileDic[file] = os.path.join(self.folder, file.replace(par2Folder, "_par2\\"))
		self.usableSizePar2 -= fsize
		return None
	
	def addDupl(self, file):
		fsize = os.path.getsize(file)
		self.fileDic[file] = os.path.join(self.folder, file.replace(duplFolder, "_dupl\\"))
		self.usableSizeDupl -= fsize
	
	def save(self):
		for forig in self.fileDic:
			fdest = self.fileDic[forig]
			os.path.exists(os.path.dirname(fdest)) or os.makedirs(os.path.dirname(fdest), exist_ok=True)
			shutil.copy(forig, fdest)
		self.writtenSize = SizeFolder(self.folder)
		self.writtenSizePar2 = SizeFolder(os.path.join(self.folder, "_par2\\"))
		self.writtenSizeDupl = SizeFolder(os.path.join(self.folder, "_dupl\\"))
		self.writtenSizeData = self.writtenSize - self.writtenSizePar2 - self.writtenSizeDupl
		print("written fold:".ljust(16, " "),
				(str(self.writtenSizeData)+" data").rjust(16, " "),
				(str(self.writtenSizePar2)+" par2").rjust(16, " "),
				(str(self.writtenSizeDupl)+" dupl").rjust(16, " "),
				(str(self.writtenSize)+" dvd").rjust(16, " ")
			)
		print("% of dvd:".ljust(16, " "),
				(str(int(10000*self.writtenSizeData/dvdSize)/100)+" % data").rjust(16, " "),
				(str(int(10000*self.writtenSizePar2/dvdSize)/100)+" % par2").rjust(16, " "),
				(str(int(10000*self.writtenSizeDupl/dvdSize)/100)+" % dupl").rjust(16, " "),
				(str(int(10000*(self.writtenSize)/dvdSize)/100) + " % dvd").rjust(16, " ")
			)
		print()

def main():
	# !!! add warning if predicted dvd size is too small (and tell how much % is possible to increase par2 size)

	if os.path.exists(outFolder):
		shutil.rmtree(outFolder)

	dataFiles = getFileList(dataFolder)
	par2Files = getFileList(par2Folder)
	duplFiles = getFileList(duplFolder)

	dataSize = SizeList(dataFiles)
	par2Size = SizeList(par2Files)
	duplSize = SizeList(duplFiles)
	storageFiles = dataSize + par2Size + duplSize

	# maxFill indicates how much the dvd can be filled with storage
	maxFill = 0.5

	n = -1
	while len(dataFiles) > 0 or len(par2Files) > 0:
		n += 1
		
		storageFiles = (SizeList(dataFiles)+SizeList(par2Files)+SizeList(duplFiles))
		dvdremaining = int(-((storageFiles) // -(maxFill * dvdSize))) # estimate needed dvd (ceiling the value)
		print(dvdremaining, "dvds to be created")
		storageXdvd = int(1.02 * storageFiles/dvdremaining) # make it a big bigger to leave some space for play
		avgdataondvd = int(storageXdvd * SizeList(dataFiles)/storageFiles)
		avgpar2ondvd = int(storageXdvd * SizeList(par2Files)/storageFiles)
		avgduplondvd = int(storageXdvd * SizeList(duplFiles)/storageFiles)
		dvd = DVD(n, avgdataondvd, avgpar2ondvd, avgduplondvd) 
		
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
		
		dvd.save()

def getFileList(folder):
	files = []
	for (root, dirs, file) in os.walk(folder):
		# !!! don't skip empty folders, add them to the list so that they will be moved to dvd
		if dirs == [] and file == []:
				print("skipping empty folder " + root)
				continue
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