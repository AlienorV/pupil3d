import logging
import sys, os, argparse, tempfile, subprocess, shutil

	
distrPath = os.path.dirname( os.path.abspath(sys.argv[0]) )

pmvsExecutable = os.path.join(distrPath, "software/pmvs/bin/pmvs2")

bundlerBinPath = ''
bundlerBinPath = os.path.join(distrPath, "software/bundler/bin_dev/")

bundler2PmvsExecutable = os.path.join(bundlerBinPath, "Bundle2PMVS")
RadialUndistordExecutable = os.path.join(bundlerBinPath, "RadialUndistort")
Bundle2VisExecutable = os.path.join(bundlerBinPath, "Bundle2Vis")

bundlerListFileName = "list.txt"

#commandLineLongFlags = ["bundlerOutputPath="]


class Pmvs():

	# currentDir = ""

	# workDir = ""
	
	# # value of command line argument --bundlerOutputPath=<..>
	# data_in = ""

	def __init__(self):
			   
		self.parseCommandLineFlags()

		# save current directory (i.e. from where RunBundler.py is called)
		self.currentDir = os.getcwd()
		# create a working directory
		self.workDir = self.data_in
		logging.info("Working directory located: "+self.workDir)
		
		if not os.path.isdir(self.data_in):
			raise Exception, "'%s' is not a directory.  Please specify a directory where bundler output files are located." % self.data_in

	def parseCommandLineFlags(self):
		parser = argparse.ArgumentParser(description="Run PMVS2 from a sparse bundler reconstruction.")
		parser.add_argument('-d', '--data_in', type=str,
			help='Give directory of bundler output path (usually located in temp folder).',
			required=True)
		parser.add_argument('-dout', '--data_out', type=str,
			help='Specify the location for the PMVS2 output (default = /pmvs).')

 		try:
			args = parser.parse_args(namespace=self)						
		except:
			parser.print_help()
			sys.exit()

	# def parseCommandLineFlags(self):
	# 	try:
	# 		opts, args = getopt.getopt(sys.argv[1:], "", commandLineLongFlags)
	# 	except getopt.GetoptError:
	# 		self.printHelpExit()

	# 	for opt,val in opts:
	# 		if opt=="--bundlerOutputPath":
	# 			self.data_in = val
	# 		elif opt=="--help":
	# 			self.printHelpExit()
		
	# 	if self.data_in=="": self.printHelpExit()
	
	def doBundle2PMVS(self):
		# just run Bundle2PMVS here
		logging.info("\nPerforming Bundler2PMVS conversion...")
		os.chdir(self.workDir)
		os.mkdir("pmvs")

		# Create directory structure
		os.mkdir("pmvs/txt")
		os.mkdir("pmvs/visualize")
		os.mkdir("pmvs/models")
		
		#$BASE_PATH/bin32/Bundle2PMVS.exe list.txt	bundle/bundle.out
		print "Running Bundle2PMVS to generate geometry and converted camera file"
		subprocess.call([bundler2PmvsExecutable, "list.txt", "./bundle/bundle.out"])
		
		# Apply radial undistortion to the images
		print "Running RadialUndistort to undistort input images"
		subprocess.call([RadialUndistordExecutable, "list.txt", "bundle/bundle.out", "pmvs"])
		
		print "Running Bundle2Vis to generate vis.dat"
		subprocess.call([Bundle2VisExecutable, "pmvs/bundle.rd.out", "pmvs/vis.dat"])

		os.chdir(os.path.join(self.workDir,"pmvs"))
		#Rename all the files to the correct name
		undistortTextFile = open("list.rd.txt", "r")
		imagesStrings = undistortTextFile.readlines()
		print "Move files in the correct directory"
		cpt = 0
		for imageString in imagesStrings:
		  image = imageString.split("/")[-1].split(".")
		  #image = imageString.split(".")
		  shutil.copy(image[0]+".rd.jpg", "visualize/%08d.jpg"%cpt)
		  shutil.copy("%08d.txt"%cpt, "txt/%08d.txt"%cpt)
		  os.remove(image[0]+".rd.jpg")
		  os.remove("%08d.txt"%cpt)
		  cpt+=1
		
		undistortTextFile.close()
		
		logging.info("Finished!")
		
	def doPMVS(self):
		print "Run PMVS2 : %s " % pmvsExecutable
		subprocess.call([pmvsExecutable, "./", "pmvs_options.txt"])
	
	# def printHelpExit(self):
	# 	self.printHelp()
	# 	sys.exit(2)
	
	def openResult(self):
		if sys.platform == "win32": subprocess.call(["explorer", self.workDir])
		else: 
			print "See the results in the '%s' directory" % self.workDir
			subprocess.call(["open", "-R", self.workDir])
	
	# def printHelp(self):
	# 	print "Error"
	# 	helpFile = open(os.path.join(distrPath, "pmvs_methods/help.txt"), "r")
	# 	print helpFile.read()
	# 	helpFile.close()
		
		
