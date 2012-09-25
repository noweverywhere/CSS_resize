#!/usr/bin/python
# Author: Marinus Swanepoel
# September 2012
# Script to convert CSS files to SCSS files in a new directory and append a 
# media query block at the endi of each file that contains all the css rules 
# and declarations with relevant pixel-measured properties multiplied for
# larger displays

import os             # module to find css files
import sys
import fileinput        # module to read files
import subprocess
try:
    import tinycss    # module to parse css
    tiny_css_loaded = True
except ImportError:
    tinyCSSLoaded = False

if tiny_css_loaded != True:
    raw_input('Dependency TinyCSS Not Installed \n Press any key to exit')
    sys.exit(1)

multiplier = 1.6
media_query = '@media (min-height: 720px) and (max-height: 1079px) {\n'
close_media_query = '}'
target_dir = './scss'
working_dir = '.'


def scan_dir(working_dir = '.'):
    """ This function runs once and start of the whole process
    It searches the specified directory and all sub-directories recusively for
    css files, if it finds a css file it parses it writes the relevant rules
    creates the media query block, creates the new file and writes the scss file
    Args:
        working_dir: String: scans the specified directory
    """
    parser = tinycss.make_parser('page3')
    for dirname, dirnames, filenames in os.walk(working_dir):
	if dirname.find('.git') != -1 or dirname.find('scss') != -1: continue
        #print 'dirname' + dirname
        for full_file_name in filenames:
            filepath = os.path.join(dirname, full_file_name)
            file_name, file_extension = os.path.splitext(filepath)
            if file_extension == '.css':
                # if we find a file with a .css extentsion
                #print '<<'+ dirname + filename
                if full_file_name.find('sencha-touch.') != -1 or full_file_name.find('jquery') != -1 or dirname.find('sencha') != -1 or dirname.find('Navigation') != -1:
                    print 'Skip ' + dirname + '/' + full_file_name 
                    continue
                #print 'Working on: ' + filepath
                rules = parseit(filepath, parser)
		        #print 'Just ran parse. Rules found are: ' + str(rules)
                contents = rewrite_rules(rules)
                if contents:
                    file_contents = str(open(filepath, 'rb').read())
                    contents = file_contents + '\n\n' + media_query + contents + close_media_query
                    #contents =    media_query + contents + close_media_query
                    #print contents
                    current_dir = file_name
                    current_dir = current_dir[:-current_dir[::-1].index('/')]
                    scssDir = makedir(current_dir + 'scss')
                    #print '++++++++++\ntarget_dir :' + target_dir
                    write_new_file(current_dir, file_name + '.scss', contents)

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
        filepath: String:    Path to the stylesheet to be parsed
        parser: TinyCSS Parser Class Instance
        returns:
        List: List of rule tuples
    """
    list_of_rules = []
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
        current_rule = {}
        current_rule['selector'] = rule.selector.as_css()                
        current_rule['hasResize'] = False        
        current_rule['declaration_list'] = []
        #print rule.selector.as_css()
        for declaration in rule.declarations:
            """ Iterate over all the declarations in the rule and store their
            values to a list. Record all the declaration properties that
            are relevant to a dict
            """
            #print declaration
            declaration_tuple = {
                'name': declaration.name,
                'valueList': [],
                'hasResize': False,
                'isImportant': declaration.priority
                }
            if declaration.name.find('background') != -1: continue
            for value in declaration.value:
                css_value = value.as_css()
                if css_value != ' ': declaration_tuple['valueList'].append(css_value)
                #print 'Value: ' + css_value
                if css_value.find('px') != -1:
                    current_rule['hasResize'] = True 
                    declaration_tuple['hasResize'] = True        
                    #print '_value: ' + value.as_css()
            current_rule['declaration_list'].append(declaration_tuple)
        list_of_rules.append(current_rule)
        current_rule = {}
    return list_of_rules


def multiply_value(value):
    """ this function breaks the declaration values passed to it down to an int
    and multiplies it with the multiplier (which may be a float) if they are
    in pixels. If the float ends in .0 we remove those trailing .0s
        Args:
            value: String: Usually formated '2px' or 'auto'
        returns: 
            string
    """
    global multiplier 
    new_value = value
    if value.find('base64') != -1:
        return value
    has_px = value.find('px')
    if has_px != -1 and value.find('(') != -1 and value.find(')') != -1:
        #print value
        start = value.index('(')
        property_name = value[0:start]
        values = value[start+1:-1]
        values = values.split(',')
        temp_sub_value_string = ''
        #print values
        for subvalue in values:
            temp_sub_value = subvalue
            #print 'subvalue is: ' + subvalue
            if subvalue.find('px') != -1:
                temp_value = int(subvalue.split('px')[0]) * multiplier
                temp_value =    str(temp_value)
                if temp_value[-2:] == '.0':
                    temp_value = temp_value[:-2]
                temp_value = temp_value + 'px'
                temp_sub_value = temp_value
            temp_sub_value_string = temp_sub_value_string + ' ' + temp_sub_value + ','
            #print 'temp_sub_value' + temp_sub_value
            #print temp_sub_value_string
        new_value = property_name + '('+ temp_sub_value_string[1:-1].replace('    ', ' ') + ')'
        #print new_value
        #raw_input('push any key to continue')
        #time.sleep(10)
    elif has_px != -1:
        #print value
        temp_value = float(value.split('px')[0]) * multiplier
        temp_value =    str(temp_value)
        if temp_value[-2:] == '.0':
            temp_value = temp_value[:-2]
            new_value = temp_value + 'px'
    return    new_value
        


def rewrite_rules(list_of_rules):
    """ Writes a big string of css rules based on the list of rule tuples supplied
    Args:
        list_of_rules: List: A list of tuples with information about css rules
    returns: 
        String: All the tuples made into a block of CSS
    """
    append_section = ''
    #print 'rules: ' + str(list_of_rules)
    for rules in list_of_rules:
        rule = rules
        #print rule
        #print '>>>'
        if rule['hasResize'] == True:
            #print 'passed' + /Navigation/resources/css/str(rule)
            append_section += '\t' + rule['selector'].replace(', ', ',\n    ') + ' {\n'
            
            for declaration in rules['declaration_list']:
                
                if declaration['hasResize'] == True:
                    #print declaration['valueList']
                    append_section += '\t\t' + declaration['name'] + ':'
                    for value in declaration['valueList']:     
                        append_section = append_section + ' ' + str(multiply_value(value))
                    
	            if declaration['isImportant'] == 'important':
                        append_section = append_section + ' !important;\n'
                    else:
                        append_section = append_section + ';\n'
                                
                                #print '$$$$$$$'
            append_section += '\t}\n\n'    
    return append_section

def write_new_file(directory, name, contents):
    """ This function writes the string contents to a new file to the path and name specified
    Args:
        directory: String: Path to directory
        name: String: name of file
        contents: String: what will be the contents of the file
    """
    #print '===========\n name:'+ name
    new_file_location = name[:-name[::-1].index('/')]
    new_file_name = name[-name[::-1].index('/'):]
    #print 'new_file_name: '+ new_file_name         
    new_file = open(new_file_location + '/scss/' + new_file_name , 'w')
    new_file.write(contents)
    new_file.close()
    print 'Wrote new file at: ' + new_file_location + 'scss/' + new_file_name    


#print 'Starting resize_css.py'
scan_dir(working_dir)
#print 'Finished resize_css.py'
sys.exit(0)
