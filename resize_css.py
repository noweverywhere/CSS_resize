#!/usr/bin/python
import os
import fileinput
import tinycss

filePathGlobal = ''
lineNumber = 0
selectorsAndRules = None
currentSelector = None
currentRule = None 
selectorMade = False
selector = ''
cssProperty = ''
propertyFinished = False
			
def makedir(dirpath):
	direxists = os.path.isdir(dirpath)
	#print "Dir exists: %r" % (direxists) 
	if direxists != True:
		scssDir = os.mkdir(dirpath) 
	scssDir = dirpath

def parseit(filepath):
	print 'opening ' + filepath
	global lineNumber
	global filePathGlobal
	lineNumber = 0
	filePathGlobal = filepath
	opfile  = open(filepath)
	words = opfile.read().replace('\n', ' ').split()
	for word in words:
		global selector
		global selectorMade
		global propertyFinished
		if selectorMade == False
			selector = selector + ' ' + word
			if word.find('{')!= -1:
				selector = selector + ' ' + word[:word.index('{')]
				selectorMade = True
				print 'we have a selector it is: ' + selector 
				word = word[word.index('{'):]
			else:
				
			if word == '' or word == ' ':
				continue
	
		cssProperty = cssProperty  + word
		if selectorMade == True:
			if word.find(':') != -1:
				cssropety
			else
				cssProperty = cssProperty + ' ' + word
	'''linesArray = opfile.readlines()
	for line in linesArray:
		global lineNumber 
		lineNumber += 1
		#print line.replace('\n','')
		analyzeLine(line)	
	'''
def getExtention(filepath):
	#print os.path.join(dirname, filename)
	fileName, fileExtension = os.path.splitext(filepath)
	#print fileExtension[1:]
	if fileExtension[1:] == 'css':
		#print 'found css file '+fileName
		parseit(filepath)

scssDir = makedir('scss')
for dirname, dirnames, filenames in os.walk('.'):
    for filename in filenames:
		filepath = os.path.join(dirname, filename)
		getExtention(filepath)
        
