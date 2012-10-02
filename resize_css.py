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
import make_styles  #import another script I made
from pprint import pprint #import pretty printing for easier debugging
import re # to find dimensional images
try:
    import tinycss    # module to parse css
    tiny_css_loaded = True
except ImportError:
    tinyCSSLoaded = False

if tiny_css_loaded != True:
    raw_input('Dependency TinyCSS Not Installed \n Press any key to exit')
    sys.exit(1)

find_dimensional_images = re.compile('\d{1,4}x\d{1,4}')
multiplier = 1.6
media_query = '@media (min-height: 720px) and (max-height: 1079px) {\n'
close_media_query = '}'
target_dir = './scss'
working_dir = '.'
prohibited_dirs = ['.git', 'scss']
prohibited_file_names = ['sencha-touch', 'jquery', 'reset', 'main_styles']
image_extentsions = ['.png', '.jpg', '.jpeg', '.gif']
missing_images_list = []

def string_in_list(item_name, prohibition_list, strict_compare):
    """ This function is used to check whether the dir or file name is 
    prohibited to help us ignore things like the jQuery UI styles etc.
        Args:
            item_name: String: name of the dir or file
            prohibition_list: List of strings
        Returns:
            Boolean: True  if item is prohibited
    """
    if strict_compare == True:
        for name in prohibition_list:
            if item_name == name:
                return True

    else:
        for name in prohibition_list:
            if item_name.find(name) != -1:
                return True
        
    return False
    

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
        has_new_scss = False
        skip = string_in_list(dirname, prohibited_dirs, False)
            #print 'skip'
        if skip == True: continue
        else:
            #print 'dirname '+ dirname
            for full_file_name in filenames:
                filepath = os.path.join(dirname, full_file_name)
                file_name, file_extension = os.path.splitext(filepath)
                if file_extension == '.css':
                    skip =  string_in_list(full_file_name, prohibited_file_names, False)
                    rules = parseit(filepath, parser)
                    contents = rewrite_rules(rules, dirname, filepath)
                    file_open = open(filepath, 'rb') 
                    file_contents = str(file_open.read())
                    file_open.close()
                    current_dir = file_name
                    current_dir = current_dir[:-current_dir[::-1].index('/')]
                    scssDir = makedir(current_dir + '/scss')
                    if skip == True:
                        write_new_file(current_dir + 'scss/', file_name + '.scss', file_contents)
                        #print 'Skip ' + dirname + '/' + full_file_name 
                        continue
                    
                    write_new_file(current_dir + 'scss/', file_name + '.scss', file_contents)
                    if contents:
                        makedir(current_dir + 'scss/720p/')
                        new_target_dir = current_dir + '/scss/720p/'
                        done = write_new_file(new_target_dir, file_name + '.scss', contents)
                    has_new_scss = True
                    #print '' + str(has_new_scss)
                    #print 'finished with css file'
            #print 'finshed loop ' + str(has_new_scss)
            if has_new_scss == True:
                #print 'Making new styles.scss'
                make_styles.make_styles(dirname, media_query)

def makedir(dirpath):
    """ this function checks that the desired dir exits, and if not creates it
    Args:
        dirpath: String: Path of desired dir
    """
    direxists = os.path.isdir(dirpath)
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
        # Make sure the rule does not have a keyword such as @import or @media
        if rule.at_keyword != None: continue
        current_rule_dict = {
            'selector': rule.selector.as_css(),
            'has_resize_or_image': False,        
            'declaration_list': [],
            'has_image': False,
            }
        for declaration in rule.declarations:
            """ Iterate over all the declarations in the rule and store their
            values to a list. Record all the declaration properties that
            are relevant to a dict
            """
            declaration_dict = {
                'name': declaration.name,
                'value_list': [],
                'has_resize_or_image': False,
                'is_important': declaration.priority,
                'has_image': False,
                'has_resize': False
                }
            for value in declaration.value:
                css_value = value.as_css()
                #if css_value.find('rgba(')!= -1:
                    #print css_value
                if css_value != ' ': declaration_dict['value_list'].append(css_value)
                if css_value.find('px') != -1:
                    current_rule_dict['has_resize_or_image'] = True 
                    declaration_dict['has_resize'] = True
                is_image = string_in_list(css_value, image_extentsions, False)
                if is_image == True:
                    current_rule_dict['has_resize_or_image'] = True
                    declaration_dict['has_image'] = True
            current_rule_dict['declaration_list'].append(declaration_dict)
        list_of_rules.append(current_rule_dict)
        current_rule_dict = {}
    return list_of_rules


def multiply_value(value, current_file_name):
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
    # ignore base64 encoded background-images that included 'px'
    if value.find('base64') != -1:
        #return the value unchanged
        return value

    #here we filter out the properties that actually have 'px' 
    #this is important for cases like this: 'border: solid red 20px;'
    has_px = value.find('px')
    
    #print value 
    
    if has_px != -1 and value.find('(') != -1 and value.find(')') != -1:
        start = value.index('(')
        property_name = value[0:start]
        values = value[start+1:-1]
        if value.find('rgba(') != -1:
            pixel_number = str(float(value[-5:-3]) * multiplier)
            return value[:-5] + pixel_number + value[-3:]
        #else: 
        values = values.split(',')
        
        temp_sub_value_string = ''
    
        for subvalue in values:
            temp_sub_value = subvalue
            #print subvalue
            if subvalue.find('px') != -1:
                temp_value = int(subvalue.split('px')[0]) * multiplier
                temp_value =    str(temp_value)
                
                if temp_value[-2:] == '.0':
                    temp_value = temp_value[:-2]
                
                temp_value = temp_value + 'px'
                temp_sub_value = temp_value
            
            temp_sub_value_string = temp_sub_value_string + ' ' + temp_sub_value + ','

        new_value = property_name + '('+ temp_sub_value_string[1:-1].replace('    ', ' ') + ')'

    elif has_px != -1:
        temp_value = float(value.split('px')[0]) * multiplier
        temp_value =    str(temp_value)

        if temp_value[-2:] == '.0':
            temp_value = temp_value[:-2]
            new_value = temp_value + 'px'

    return new_value

def make_new_relative_path(starting_path, path):
    new_path = path.replace('img/', 'img/720p/')
    dimensional_match = find_dimensional_images.search(new_path)
    if dimensional_match:
        start = dimensional_match.start()
        end = dimensional_match.end()
        dimensions = new_path[start:end]
        divider = dimensions.index('x')
        width = float(dimensions[0:divider]) * multiplier
        height = float(dimensions[divider+1:]) * multiplier
        width = str(width)[:-2]
        height = str(height)[:-2]
        new_path = new_path[:start] + width + 'x' + height + new_path[end:]
    path_parts = new_path.split('..')
    #pprint(path_parts)
    dirs_up = len(path_parts)
    start_path_segments = starting_path.split('/')
    modified_path_start = '/'.join(start_path_segments[:-(dirs_up - 1)])
    modified_path = starting_path[:starting_path.rfind('/')] + path_parts[-1]
    #print 'Modified path: ' + modified_path
    file_exists = os.path.isfile(modified_path)
    #new_path = path
    return (file_exists, new_path, modified_path)

def log_missing_image(missing_image_path):
    global missing_images_list
    already_found_missing = string_in_list(missing_image_path, missing_images_list, True)
    if already_found_missing == False:
        missing_images_list.append(missing_image_path)
    #print missing_image_path


def process_image(declaration_list, css_file_dir):
    #pprint(declaration_list)
    declaration_string = ''
    for paramater in declaration_list:
        #print paramater
        if paramater.find('url') != -1 and True == string_in_list(paramater, image_extentsions, False):
            #print 'path is this: ' + paramater
            path = paramater
            img_720p_exists, modified_path, real_path = make_new_relative_path(css_file_dir, paramater[4:-1])
            if img_720p_exists == True:
                #print '::: File exists: ' + modified_path
                declaration_string = declaration_string + ' url(\'' + modified_path + ')'
            else:
                declaration_string = declaration_string + ' ' + paramater
                #print '::: File does not exits: ' + modified_path
                log_missing_image(real_path)
                #print '\n'
        else:
            declaration_string = declaration_string + ' ' + paramater

        declaration_string = declaration_string + ''
    return declaration_string


def rewrite_rules(list_of_rules, file_dir, file_name):
    """ Writes a big string of css rules based on the list of rule tuples supplied
    Args:
        list_of_rules: List: A list of tuples with information about css rules
    returns: 
        String: All the tuples made into a block of CSS
    """
    append_section = ''
    for rules in list_of_rules:
        rule = rules
        if rule['has_resize_or_image'] == True:
            append_section += '\t' + rule['selector'].replace(', ', ',\n\t') + '{\n'

            for declaration in rules['declaration_list']:
                #print('\ndeclaration: ')
                #pprint(declaration)
                #if declaration['has_resize'] == True and  declaration['has_image'] == True:
                    #pprint(declaration)

                if declaration['has_resize'] == True:
                    append_section = append_section + '\t\t' + declaration['name'] + ':'
                    for value in declaration['value_list']:     
                        append_section = append_section + ' ' + multiply_value(value, file_name)

                    if declaration['is_important'] == 'important':
                        append_section = append_section + ' !important;\n'
                    else:
                        append_section = append_section + ';\n'

                if declaration['has_image'] == True:
                    #print '\n'
                    #pprint(declaration)
                    append_section = append_section + '\t\t' + declaration['name'] + ':'
                    append_section = append_section + ' ' + process_image(declaration['value_list'], file_dir)
                    if declaration['is_important'] == 'important':
                        append_section = append_section + ' !important;\n'
                    else:
                        append_section = append_section + ';\n'
                                
            append_section += '\t}\n\n'
    return append_section

def write_new_file(directory, name, contents):
    """ This function writes the string contents to a new file to the path and name specified
    Args:
        directory: String: Path to directory
        name: String: name of file
        contents: String: what will be the contents of the file
    """
    #print '===========\n name:'+ directory + '/' + name 
    new_file_location = directory.replace('//', '/')
    new_file_name = name[-name[::-1].index('/'):]
    #print 'new_file' + new_file_location + ' && ' + new_file_name
    new_file = open(new_file_location +  new_file_name , 'w')
    new_file.write(contents)
    new_file.close()
    #print 'Wrote new file at: ' + new_file_location +  new_file_name
    return 'Done'

def write_logs():
    if any(missing_images_list) == True:
        missing_images_log = open('missing_images.txt', 'w')
        missing_images_log.write('\n'.join(missing_images_list) + '\n')
        missing_images_log.close()

if __name__ == '__main__':
    # If this is the main script being called
    #print 'Starting resize_css.py'
    scan_dir(working_dir)
    write_logs()
    #print 'Finished resize_css.py'
    sys.exit(0)
