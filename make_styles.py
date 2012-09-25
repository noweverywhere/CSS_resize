#!/usr/bin/python
# Author: Marinus Swanepoel
# September 2012
# Script to make scss files and one to import them all.

import json #import module to read json config file
from pprint import pprint #import pretty print for simple debugging
from os import path

def make_styles(working_dir='.'):
    print 'making styles'
    print working_dir 
    json_css_order = open(working_dir + '/order.json')
    print 
    css_order = json.load(json_css_order)
    pprint(css_order)
    json_css_order.close()
    contents = create_media_queries(css_order)
    make_file(working_dir + 'test.txt', contents)

def create_media_queries(css_order_json, media_query_str):
    contents = media_query_str
    for css_file_name in css_order_json['cssfilenames']:
        if os.path.exists(working_dir + '/720p/' + css_file_name + '.scss'):
            contents = contents + '\n@import "' + css_file_name + '";'
    return contents

def make_file(path, contents):
    new_file = open(path, 'w')
    new_file.write(contents)
    new_file.close()

if __name__ == '__main__':
    # test1.py executed as script
    # do something
    make_styles()
