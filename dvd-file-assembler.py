import os, shutil

dataFolder = ".\\example\\data\\"	# folder where data is stored and must be splitted on multiple dvds
par2Folder = ".\\example\\par2\\"	# folder where par2 data is stored and must be splitted on multiple dvds
duplFolder = ".\\example\\dupl\\"	# folder where data must be present on all dvds
outFolder  = ".\\out\\"

dvdSize = 500000000

class DVD():
	def __init__(self, id, dataFolderSize, par2FolderSize, duplFolderSize):
		self.usableSizeData = (dvdSize - duplFolderSize) * (dataFolderSize / (dataFolderSize + par2FolderSize))
		self.usableSizePar2 = (dvdSize - duplFolderSize) * (par2FolderSize / (dataFolderSize + par2FolderSize))
		self.usableSizeDupl = duplFolderSize
		self.id = id
		self.folder = os.path.join(outFolder, "dvd" + str(self.id))
		os.path.exists(outFolder) or os.makedirs(outFolder, exist_ok=True)
		os.path.exists(self.folder) or os.makedirs(self.folder, exist_ok=True)
	
	def addData(self, file, fsize):
		fileOut = os.path.join(self.folder, file.replace(dataFolder, ""))
		print("\t".join([file, fileOut, str(fsize)])) # !!!
		os.path.exists(os.path.dirname(fileOut)) or os.makedirs(os.path.dirname(fileOut), exist_ok=True)
		shutil.copy(file, fileOut)
		self.usableSizeData -= fsize

	def addPar2(self, file, fsize):
		fileOut = os.path.join(self.folder, file.replace(par2Folder, "_par2\\"))
		print("\t".join([file, fileOut, str(fsize)])) # !!!
		os.path.exists(os.path.dirname(fileOut)) or os.makedirs(os.path.dirname(fileOut), exist_ok=True)
		shutil.copy(file, fileOut)
		self.usableSizePar2 -= fsize
	
	def addDupl(self, file, fsize):
		fileOut = os.path.join(self.folder, file.replace(duplFolder, "_dupl\\"))
		print("\t".join([file, fileOut, str(fsize)])) # !!!
		os.path.exists(os.path.dirname(fileOut)) or os.makedirs(os.path.dirname(fileOut), exist_ok=True)
		shutil.copy(file, fileOut)
		self.usableSizeDupl -= fsize

def main():
	dataFolderSizeToCopy = Size(dataFolder)
	par2FolderSizeToCopy = Size(par2Folder)
	duplFolderSizeToCopy = Size(duplFolder)

	dataFiles = getFileList(dataFolder)
	par2Files = getFileList(par2Folder)
	duplFiles = getFileList(duplFolder)

	n = -1
	while len(dataFiles) > 0 or len(par2Files) > 0:
		n += 1
		dvd = DVD(n, dataFolderSizeToCopy, par2FolderSizeToCopy, duplFolderSizeToCopy)
		
		for f in duplFiles:
			fsize = os.path.getsize(f)
			dvd.addDupl(f, fsize)
		
		for f in dataFiles:
			fsize = os.path.getsize(f)
			if dvd.usableSizeData < fsize:
				break
			dvd.addData(f, fsize)
			dataFiles.remove(f)
			dataFolderSizeToCopy -= fsize
		
		for f in par2Files:
			fsize = os.path.getsize(f)
			if dvd.usableSizePar2 < fsize:
				break
			dvd.addPar2(f, fsize)
			par2Files.remove(f)
			par2FolderSizeToCopy -= fsize

def getFileList(folder):
	files = []
	for (root, dirs, file) in os.walk(folder):
		if dirs == [] and file == []:
				print("skipping empty folder " + root)
				continue
		for f in file:
			files.append(os.path.join(root, f))
	files.sort()
	return files

def Size(Folderpath):
	print("calculating size of " + Folderpath + "...\t", end="")
	size = 0
	for path, dirs, files in os.walk(Folderpath):
		for f in files:
			fp = os.path.join(path, f)
			size += os.path.getsize(fp)
	print(size)
	return size

if __name__ == "__main__":
	main()