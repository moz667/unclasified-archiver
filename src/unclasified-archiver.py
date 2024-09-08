#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unclasified_archiver import archive_all

import configparser
import getopt
import io
import os
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
        for line in sys.stdin:
            config_file += line
        
        config_file = io.StringIO(config_file)

    if not config_file:
        if not os.path.isfile('config.ini'):
            print_help()
            sys.exit(2)
        else:
            config_file = 'config.ini'

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
        ignore_no_media_files = False if not 'ignore_no_media_files' in cfg_section or cfg_section['ignore_no_media_files'] != 'true' else True
        resilio_trashed_files = False if not 'resilio_trashed_files' in cfg_section or cfg_section['resilio_trashed_files'] != 'true' else True
        resilio_backup = False if not 'resilio_backup' in cfg_section or cfg_section['resilio_backup'] != 'true' else True

        if resilio_backup:
            move_files = False
            delete_empty_dir = False
            ignore_no_media_files = True
            resilio_trashed_files = True


        if __debug__:
            print(' * %s' % section_key)
            print('   - unclasified_folder: %s' % unclasified_folder)
            print('   - archive_folder: %s' % archive_folder)
            print('   - move_files: %s' % move_files)
            print('   - delete_empty_dir: %s' % delete_empty_dir)
            print('   - ignore_no_media_files: %s' % ignore_no_media_files)
            print('   - resilio_trashed_files: %s' % resilio_trashed_files)
            print('   - resilio_backup: %s' % resilio_backup)
        
        # Archivar
        archive_all(
            source_folder=unclasified_folder, 
            target_folder=archive_folder, 
            move_files=move_files, 
            delete_empty_dir=delete_empty_dir,
            ignore_no_media_files=ignore_no_media_files,
            resilio_trashed_files=resilio_trashed_files,
            dry_run=dry_run
        )

def print_help():
    print('Help:')
    print('    unclasified-archiver.py [--c=<config-file.ini>] [--dry-run]')
    print('    unclasified-archiver.py [--config=<config-file.ini>] [--dry-run]')

if __name__ == "__main__":
    main()

