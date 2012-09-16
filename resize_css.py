#!/usr/bin/python
import os		# module to find css files
import fileinput	# module to read files
#import re 		# module to use regex
try:
	import tinycss	# module to parse css
	tinyCSSLoaded = True
except ImportError:
	tinyCSSLoaded = False

if tinyCSSLoaded != True:
	os.exit('Dependency TinyCSS Not Insalled')

multiplier = 1.6
filePathGlobal = ''
lineNumber = 0
rulesList = []
currentRule = {}
currentDeclaration = ''
currentValue = None
mediaQuery = '@media (min-height: 395px) and (max-height: 719px) {\n'
closeMediaQuery = '}'
targetDir = '/scss'
parser = tinycss.make_parser('page3')	


def scanDir():
	for dirname, dirnames, filenames in os.walk('.'):
		for filename in filenames:
			filepath = os.path.join(dirname, filename)
			fileName, fileExtension = os.path.splitext(filepath)
			if fileExtension == '.css':
				#print '<<'+ dirname + filename
				parseit(filepath)
				contents = rewriteRules()
				if contents:
					contents = open(filepath, 'r').read() + mediaQuery + contents + closeMediaQuery
					print contents
					writeNewFile(dirname + targetDir, fileName + '.scss', contents)


def makedir(dirpath):
	direxists = os.path.isdir(dirpath)
	#print "Dir exists: %r" % (direxists) 
	if direxists != True:
		scssDir = os.mkdir(dirpath) 
	scssDir = dirpath

def parseit(filepath):
	global parser
	global currentRule
	global multiplier
	stylesheet = parser.parse_stylesheet_file(filepath)
	for rule in stylesheet.rules:
		#print 'rulez: ' + str(rule)
		#print dir(rule)
		currentRule['selector'] = rule.selector.as_css()		
		currentRule['hasResize'] = False	
		currentRule['declarationList'] = []
		#print rule.selector.as_css()
		for declaration in rule.declarations:
			#print declaration
			declarationTuple = {}
			declarationTuple['name'] =  declaration.name
			declarationTuple['valueList'] = []
			declarationTuple['hasResize'] = False	
			#print 'declaration name: ' + declaration.name
			for value in declaration.value:
				valueCSS = value.as_css()		
				declarationTuple['valueList'].append(valueCSS)
				#print 'Value: ' + valueCSS
				if valueCSS.find('px') != -1:
					currentRule['hasResize'] = True	
					declarationTuple['hasResize'] = True	
					#print '_value: ' + value.as_css()
					value.value * multiplier	
			currentRule['declarationList'].append(declarationTuple)
		rulesList.append(currentRule)
		currentRule = {}

def getExtention(filepath):
	#print os.path.join(dirname, filename)
	#print fileExtension[1:]
	return fileExtension[1:]
		#print 'found css file '+fileName

def multiplyValue(value):
	global multiplier 
	if value.find('px') != -1:
		tempValue = int(value.split('px')[0]) * multiplier
		tempValue =  str(tempValue)
		if tempValue[-2:] == '.0':
			tempValue = tempValue[:-2]
		newValue = tempValue + 'px'
	else:
		tempValue = value.replace(' ', '')
		newValue = tempValue
	return  newValue
	

scssDir = makedir('scss')

def rewriteRules():
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
						appendSection += ' ' + str(multiplyValue(value))
					appendSection += ';\n'
					#print '$$$$$$$'
			appendSection += '\t}\n\n'	
	return appendSection

def writeNewFile(directory, name, contents):
	newFile = open(directory + '/' + name, 'w')
	newFile.write(contents)
	newFile.close()


scanDir()
		
#print '0000000000000\n' + appendSection
