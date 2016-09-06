#!/usr/bin/env python3

import os
import glob
import subprocess

CSS_OUTPUT_DIR = 'build/static/css'

#---------------------------------------------------------------------
def main():
    print('Compiling less files...')
    less_files = glob.glob('less/*.less')
    if not os.path.exists(CSS_OUTPUT_DIR):
        os.makedirs(CSS_OUTPUT_DIR)
    for less_file in less_files:
        basename = os.path.splitext(os.path.basename(less_file))[0]
        css_file = os.path.join(CSS_OUTPUT_DIR, basename + '.css')
        print('Compiling %s -> %s...' % (less_file, css_file))
        subprocess.check_call(['lessc', less_file, css_file])

#---------------------------------------------------------------------
if __name__ == '__main__':
    main()
