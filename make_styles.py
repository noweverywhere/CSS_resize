#!/usr/bin/python
# Author: Marinus Swanepoel
# September 2012
# Script to make scss files and one to import them all.

import json #import module to read json config file
from pprint import pprint #import pretty print for simple debugging
import os
from subprocess import check_call
from subprocess import call

def make_styles(working_dir='.', media_query='@media....'):
    """ This is the main function for this script
    For this to work I expect that the user has created a json file that 
    lists the css files to be concatenated in order.
    """
    #print 'making styles'
    # if we dont have a order json file dont do anything
    #print ">>>>>" + working_dir + '/order.json'
    if False == os.path.isfile(working_dir + '/order.json'): return
    final_block = ''
    json_css_order = open(working_dir + '/order.json')
    css_order = json.load(json_css_order)
    json_css_order.close()
    final_block, import_block_720 = create_import_blocks(css_order, working_dir)
    if import_block_720:
            final_block = final_block + '\n\n' + media_query + import_block_720 + '\n}\n'
    make_file(working_dir + '/scss/' + 'main_styles.scss', final_block + '\n')
    call_sass(working_dir)

def create_import_blocks(css_order_json, working_dir):
    import_block = ''
    import_block_720 = ''
    for css_file_name in css_order_json['cssfilenames']:
        comment_block = '\n/**\n *  File:' + css_file_name + '.scss\n **/'
        import_block =  import_block + comment_block + '\n@import "' + css_file_name + '";\n'
        #print comment_block
        desired_path = working_dir + '/scss/720p/' + css_file_name + '.scss'
        has_720p_version =  os.path.exists(desired_path)
        #print desired_path + ' exists: ' + str(has_720p_version)
        if has_720p_version == True:
            import_block_720 = import_block_720 + comment_block + '\n\t@import ' + '"720p/' +css_file_name + '";\n' 
    return (import_block, import_block_720)

def make_file(path, contents):
    new_file = open(path, 'w')
    new_file.write(contents)
    new_file.close()

def call_sass(path):
    path = path[2:]
    css_file_path = path + '/main_styles.css'
    #print 'DOES IT EXIT? '+ css_file_path 
    if os.path.isfile(css_file_path ) != True:
        new_file = open(css_file_path, 'w')
        new_file.write('')
        new_file.close()
    #print 'I AM GOING TO CALL SASS HERE: ' + path
    #call('pwd')
    command = 'sass --update '+ path + '/scss/main_styles.scss:' + path + '/main_styles.css --style expanded'
    print command
    #check_call(command)

if __name__ == '__main__':
    # test1.py executed as script
    # do something
    make_styles()
