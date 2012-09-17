#!/usr/bin/python
# Author: Marinus Swanepoel
# September 2012
# Script to convert CSS files to SCSS files in a new directory and append a 
# media query block at the endi of each file that contains all the css rules 
# and declarations with relevant pixel-measured properties multiplied for
# larger displays

import os		# module to find css files
import fileinput	# module to read files
try:
	import tinycss	# module to parse css
	tinyCSSLoaded = True
except ImportError:
	tinyCSSLoaded = False

if tinyCSSLoaded != True:
	raw_input('Dependency TinyCSS Not Installed \n Press any key to exit')

multiplier = 1.6
mediaQuery = '@media (min-height: 395px) and (max-height: 719px) {\n'
closeMediaQuery = '}'
targetDir = './scss'
workingDir = '.'


def scanDir(workingDir = '.'):
	""" This function runs once and start of the whole process
	It searches the specified directory and all sub-directories recusively for
	css files, if it finds a css file it parses it writes the relevant rules
	creates the media query block, creates the new file and writes the scss file
		Args:
			workingDir: String: scans the specified directory
	"""
	parser = tinycss.make_parser('page3')
	for dirname, dirnames, filenames in os.walk(workingDir):
		print 'dirname' + dirname
		for filename in filenames:
			if filename.find('sencha-touch.') != -1: continue
			filepath = os.path.join(dirname, filename)
			fileName, fileExtension = os.path.splitext(filepath)
			if fileExtension == '.css':
				# if we find a file with a .css extentsion
				#print '<<'+ dirname + filename
				print 'Working on: ' + filepath
				rules = parseit(filepath, parser)
				contents = rewriteRules(rules)
				if contents:
					contents = open(filepath, 'r').read() + '\n' + mediaQuery + contents + closeMediaQuery
					#print contents
					currentDir = fileName
					currentDir = currentDir[:-currentDir[::-1].index('/')]
					scssDir = makedir(currentDir + 'scss')
					#print '++++++++++\ntargetDir :' + targetDir
					writeNewFile(currentDir, fileName + '.scss', contents)


def makedir(dirpath):
	""" this function checks that the desired dir exits, and if not creates it
		Args:
			dirpath: String: Path of desired dir
	"""
	#print 'making dir at: ' + dirpath
	direxists = os.path.isdir(dirpath)
	#print "Dir exists: %r" % (direxists) 
	if direxists != True: scssDir = os.mkdir(dirpath) 

def parseit(filepath, parser):
	""" this function calls the CSS parser from TinyCSS to create a stylesheet object
	that we then iterate over recording the relevant css rules and declarations
		Args:
			filepath: String:  Path to the stylesheet to be parsed
			parser: TinyCSS Parser Class Instance
		returns:
			List: List of rule tuples
	"""
	rulesList = []
	stylesheet = parser.parse_stylesheet_file(filepath)
	for rule in stylesheet.rules:
		""" Iterate over all the rules in the stylesheet by default we 
		assume that there are no rules that will need to be resized
		we store all the information in a dict that we push to a list
		"""
		#print 'rulez: ' + str(rule)
		#print dir(rule)
		# Make sure the rule does not have a keyword such as @import or @media
		if rule.at_keyword != None: continue
		currentRule = {}
		currentRule['selector'] = rule.selector.as_css()		
		currentRule['hasResize'] = False	
		currentRule['declarationList'] = []
		#print rule.selector.as_css()
		for declaration in rule.declarations:
			""" Iterate over all the declarations in the rule and store their
			values to a list. Record all the declaration properties that
			are relevant to a dict
			"""
			#print declaration
			declarationTuple = {
				'name': declaration.name,
				'valueList': [],
				'hasResize': False,
				'isImportant': declaration.priority
				}
			for value in declaration.value:
				valueCSS = value.as_css()
				if valueCSS != ' ': declarationTuple['valueList'].append(valueCSS)
				#print 'Value: ' + valueCSS
				if valueCSS.find('px') != -1:
					currentRule['hasResize'] = True	
					declarationTuple['hasResize'] = True	
					#print '_value: ' + value.as_css()
			currentRule['declarationList'].append(declarationTuple)
		rulesList.append(currentRule)
		currentRule = {}
	return rulesList


def multiplyValue(value):
	""" this function breaks the declaration values passed to it down to an int
	and multiplies it with the multiplier (which may be a float) if they are
	in pixels. If the float ends in .0 we remove those trailing .0s
		Args:
			value: String: Usually formated '2px' or 'auto'
		returns: 
			string
	"""
	global multiplier 
	newValue = value
	if value.find('px') != -1:
		tempValue = int(value.split('px')[0]) * multiplier
		tempValue =  str(tempValue)
		if tempValue[-2:] == '.0':
			tempValue = tempValue[:-2]
		newValue = tempValue + 'px'
	return  newValue
	


def rewriteRules(rulesList):
	""" Writes a big string of css rules based on the list of rule tuples supplied
		Args:
			rulesList: List: A list of tuples with information about css rules
		returns: 
			String: All the tuples made into a block of CSS
	"""
	appendSection = ''
	for rules in rulesList:
		rule = rules
		#print rule
		#print '>>>'
		if rule['hasResize'] == True:
			#print 'passed' + str(rule)
			appendSection += '\t' + rule['selector'].replace(', ', ',\n\t') + ' {\n'
			for declaration in rules['declarationList']:
				if declaration['hasResize'] == True:
					#print declaration['valueList']
					appendSection += '\t\t' + declaration['name'] + ':'
					for value in declaration['valueList']:   
						appendSection = appendSection + ' ' + str(multiplyValue(value))
					if declaration['isImportant'] == 'important':
						appendSection = appendSection + ' !important;\n'
					else:
						appendSection = appendSection + ';\n'
						
					#print '$$$$$$$'
			appendSection += '\t}\n\n'	
	return appendSection

def writeNewFile(directory, name, contents):
	""" This function writes the string contents to a new file to the path and name specified
		Args:
			directory: String: Path to directory
			name: String: name of file
			contents: String: what will be the contents of the file
	
	"""
	#print '===========\n name:'+ name
	newFileLocation = name[:-name[::-1].index('/')]
	newFileName = name[-name[::-1].index('/'):]
	#print 'newFileName: '+ newFileName 	
	newFile = open(newFileLocation + '/scss/' + newFileName , 'w')
	newFile.write(contents)
	newFile.close()
	print 'Wrote new file at: ' + newFileLocation + '/scss/' + newFileName  


scanDir(workingDir)
