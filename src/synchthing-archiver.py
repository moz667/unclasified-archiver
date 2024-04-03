#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Libraries

import getopt, sys
import configparser

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:v", ["help", "config="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    
    config_file = 'config.ini'
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
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
        # Archivar
        print(cfg_section)

def usage():
    # TODO:
    print("TODO: Usage")

def archive(source_folder, target_folder, move_files=True):
    pass

if __name__ == "__main__":
    main()

