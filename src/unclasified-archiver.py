#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unclasified_archiver import archive_all

import configparser
import fileinput
import getopt
import io
import sys

def main():
    dry_run = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc", ["dry-run", "help", "config="])
    except getopt.GetoptError as err:
        print(err)
        print_help()
        sys.exit(2)
    
    config_file = ''
    
    for o, a in opts:
        if o == "--dry-run":
            dry_run = True
        elif o in ("-h", "--help"):
            print_help()
            sys.exit()
        elif o in ("-c", "--config"):
            config_file = a
        else:
            assert False, "unhandled option"

    if not config_file and not sys.stdin.isatty():
        for line in fileinput.input():
            config_file += line
        
        config_file = io.StringIO(config_file)

    if not config_file:
        print_help()
        sys.exit(2)

    config = configparser.ConfigParser()
    
    if isinstance(config_file, io.StringIO):
        config.read_file(config_file)
    else:
        config.read(config_file)

    for section_key in config.sections():
        cfg_section = config[section_key]

        unclasified_folder = cfg_section['unclasified_folder']
        archive_folder = cfg_section['archive_folder']
        move_files = True if not 'move_files' in cfg_section or cfg_section['move_files'] != 'false' else False
        delete_empty_dir = True if not 'delete_empty_dir' in cfg_section or cfg_section['delete_empty_dir'] != 'false' else False

        if __debug__:
            print(' * %s' % section_key)
            print('   - unclasified_folder: %s' % unclasified_folder)
            print('   - archive_folder: %s' % archive_folder)
            print('   - move_files: %s' % move_files)
            print('   - delete_empty_dir: %s' % delete_empty_dir)
        
        # Archivar
        archive_all(
            source_folder=unclasified_folder, 
            target_folder=archive_folder, 
            move_files=move_files, 
            delete_empty_dir=delete_empty_dir,
            dry_run=dry_run
        )

def print_help():
    print('unclasified-archiver.py --c=<config-file.ini> [--dry_run]')

if __name__ == "__main__":
    main()

