import os, shutil

dataFolder = ".\\example\\data\\"	# folder where data is stored and must be splitted on multiple dvds
par2Folder = ".\\example\\par2\\"	# folder where par2 data is stored and must be splitted on multiple dvds
duplFolder = ".\\example\\dupl\\"	# folder where data must be present on all dvds
outFolder  = ".\\out\\"

dvdSize = 500000000

class DVD():
	def __init__(self, id, dataFolderSize, par2FolderSize, duplFolderSize):
		self.usableSizeData = int((dvdSize - duplFolderSize) * (dataFolderSize / (dataFolderSize + par2FolderSize)))
		self.usableSizePar2 = int((dvdSize - duplFolderSize) * (par2FolderSize / (dataFolderSize + par2FolderSize)))
		self.usableSizeDupl = duplFolderSize
		self.id = id
		self.folder = os.path.join(outFolder, "dvd" + str(self.id))
		self.fileDic = {}
		os.path.exists(outFolder) or os.makedirs(outFolder, exist_ok=True)
		os.path.exists(self.folder) or os.makedirs(self.folder, exist_ok=True)
		print(("DVD"+str(self.id)+" reserved:").ljust(14, " "), (str(self.usableSizeData)+" data").rjust(15, " "), (str(self.usableSizePar2)+" par2").rjust(15, " "), (str(self.usableSizeDupl)+" dupl").rjust(15, " "))
	
	def addData(self, file, fsize):
		if self.usableSizeData < fsize:
			return "file too big"
		self.fileDic[file] = os.path.join(self.folder, file.replace(dataFolder, ""))
		self.usableSizeData -= fsize
		return None

	def addPar2(self, file, fsize):
		if self.usableSizePar2 < fsize:
			return "file too big"
		self.fileDic[file] = os.path.join(self.folder, file.replace(par2Folder, "_par2\\"))
		self.usableSizePar2 -= fsize
		return None
	
	def addDupl(self, file, fsize):
		self.fileDic[file] = os.path.join(self.folder, file.replace(duplFolder, "_dupl\\"))
		self.usableSizeDupl -= fsize
	
	def save(self):
		for forig in self.fileDic:
			fdest = self.fileDic[forig]
			os.path.exists(os.path.dirname(fdest)) or os.makedirs(os.path.dirname(fdest), exist_ok=True)
			shutil.copy(forig, fdest)
		print("folder size:".ljust(14, " "),
				# !!! add log: % of data+par2 dedicated to par2 folder
				(str(SizeFolder(self.folder, exclude=["_par2\\", "_dupl\\"])) + " data").rjust(15, " "),
				(str(SizeFolder(os.path.join(self.folder, "_par2\\"))) + " par2").rjust(15, " "),
				(str(SizeFolder(os.path.join(self.folder, "_dupl\\"))) + " dupl").rjust(15, " "))
		print("dvd size:".ljust(14, " "),
				(str(SizeFolder(self.folder)) + " data").rjust(15, " ")),
		print()

def main():
	dataFiles = getFileList(dataFolder)
	par2Files = getFileList(par2Folder)
	duplFiles = getFileList(duplFolder)

	# !!! add prediction for how many dvd (and confirmation)
	# !!! make so that all dvd have same size
	# !!! add warning if predicted dvd size is too small (and tell how much % is possible to increase par2 size)

	n = -1
	while len(dataFiles) > 0 or len(par2Files) > 0:
		n += 1
		dvd = DVD(n, SizeList(dataFiles), SizeList(par2Files), SizeList(duplFiles))
		
		for f in duplFiles:
			dvd.addDupl(f, os.path.getsize(f))
	
		for f in dataFiles[:]: # iterate over copy of list
			err = dvd.addData(f, os.path.getsize(f))
			if err != None:
				break
			dataFiles.remove(f)
		
		for f in par2Files[:]: # iterate over copy of list
			err = dvd.addPar2(f, os.path.getsize(f))
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