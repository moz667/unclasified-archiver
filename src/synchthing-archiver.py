#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.files import SyncArchFile, archive_file

import getopt, os, sys
import configparser

verbose = False
dry_run = False

def main():
    global verbose, dry_run

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:v", ["dry-run", "help", "config="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    
    config_file = 'config.ini'
    
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o == "--dry-run":
            dry_run = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-c", "--config"):
            config_file = a
        else:
            assert False, "unhandled option"

    # TODO:
    # Leer configuracion
    config = configparser.ConfigParser()
    config.read(config_file)
    
    for section_key in config.sections():
        cfg_section = config[section_key]

        stversions_folder = cfg_section['stversions_folder']
        archive_folder = cfg_section['archive_folder']
        move_files = True if not 'move_files' in cfg_section or cfg_section['move_files'] != 'false' else False
        if verbose:
            print(' * %s' % section_key)
            print('   - stversions_folder: %s' % stversions_folder)
            print('   - archive_folder: %s' % archive_folder)
            print('   - move_files: %s' % move_files)

        
        # Archivar
        archive_all(source_folder=stversions_folder, target_folder=archive_folder, move_files=move_files)

def usage():
    # TODO:
    print("TODO: Usage")

def archive_all(source_folder, target_folder, move_files=True):
    if not os.path.exists(source_folder):
        print("ERROR: Directory '%s' not exists" % [source_folder])
        sys.exit(2)
    
    if not os.path.exists(target_folder):
        print("ERROR: Directory '%s' not exists" % [target_folder])
        sys.exit(2)

    for dirpath, dirs, files in os.walk(source_folder):
        if verbose:
            print("     + source: %s" % dirpath)
        
        for dir in dirs:
            archive_all(
                source_folder=dir, 
                target_folder=target_folder, 
                move_files=move_files
            )

        for file in files:
            if verbose:
                print("       * file: %s" % file)
            
            sync_arch_file = SyncArchFile(file=os.path.join(dirpath, file))

            archive_target_folder = target_folder
            archive_date = sync_arch_file.get_meta_datec()

            if verbose and not archive_date is None:
                print("         - exif date: %s" % archive_date)

            if archive_date is None:
                archive_date = sync_arch_file.get_filename_datec()
                if verbose and not archive_date is None:
                    print("         - filename date: %s" % archive_date)
            

            if archive_date is None:
                archive_date = sync_arch_file.get_file_datec()
                archive_target_folder = os.path.join(target_folder, 'unclasified')

                if verbose and not archive_date is None:
                    print("         - `unclasified` file creation date: %s" % archive_date)
            
            if not archive_file(
                sync_arch_file=sync_arch_file, 
                archive_target_folder=archive_target_folder, 
                archive_date=archive_date,
                move_files=move_files,
                dry_run=dry_run
            ):
                sys.exit(2)

if __name__ == "__main__":
    main()

