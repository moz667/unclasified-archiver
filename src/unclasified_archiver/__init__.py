#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime, hashlib, os, shutil

import exifread
from exif import Image
import ffmpeg
from pymediainfo import MediaInfo
import whatimage

class SyncArchFile:
    TYPE_IMAGE = 'Image'
    TYPE_VIDEO = 'Video'
    TYPE_AUDIO = 'Audio'
    TYPE_OTHER = 'Other'
    
    def __init__(self, file):
        self.file = file
        self.filename = os.path.basename(file)

        self.file_type = None
        self.sha1 = None

        self.meta_datec = None
        self.file_datec = None
        self.filename_datec = None

    def get_file(self):
        return self.file
    
    def get_filename(self):
        return self.filename

    def get_file_type(self):
        if self.file_type is None:
            self.calculate_file_type()
        
        return self.file_type

    def calculate_file_type(self):
        self.file_type = None
        media_info = MediaInfo.parse(self.file)

        for track in media_info.tracks:
            if track.track_type == self.TYPE_IMAGE or \
                track.track_type == self.TYPE_VIDEO:

                self.file_type = track.track_type
        
        if self.file_type is None:
            for track in media_info.tracks:
                if track.track_type == self.TYPE_AUDIO:
                    self.file_type = track.track_type

        if self.file_type is None:
            self.file_type = self.TYPE_OTHER

    def get_sha1(self):
        if self.sha1 is None:
            self.calculate_sha1()

        return self.sha1

    def calculate_sha1(self):
        openedFile = open(self.file, 'rb')
        readFile = openedFile.read()
        self.sha1 = hashlib.sha1(readFile).hexdigest()
    
    def get_meta_datec(self):
        if self.meta_datec is None:
            self.calculate_meta_datec()
        
        return self.meta_datec

    def calculate_meta_datec(self):
        self.meta_datec = None

        if self.get_file_type() in [self.TYPE_VIDEO, self.TYPE_AUDIO]:
            vid_probe = ffmpeg.probe(self.file)

            if "streams" in vid_probe:
                for track in vid_probe['streams']:
                    if 'tags' in track and 'creation_time' in track['tags']:
                        self.meta_datec = datetime.datetime.strptime(
                            track['tags']['creation_time'], '%Y-%m-%dT%H:%M:%S.%fZ'
                        )
                        break
        elif self.get_file_type() == self.TYPE_IMAGE:
            try:
                f = open(self.file, 'rb')
                
                fmt = whatimage.identify_image(f.read())
                
                str_datetime = None

                if fmt == 'heic':
                    tags = exifread.process_file(f)
                    str_datetime = tags['EXIF DateTimeOriginal'].__str__()
                else:
                    exif_image = Image(f)
                    
                    if exif_image.has_exif:
                        str_datetime = exif_image.datetime
                
                if not str_datetime is None:
                    self.meta_datec = datetime.datetime.strptime(
                        str_datetime, '%Y:%m:%d %H:%M:%S'
                    )
            except:
                pass

    def get_file_datec(self):
        if self.file_datec is None:
            self.calculate_file_datec()
        
        return self.file_datec

    def calculate_file_datec(self):
        self.file_datec = datetime.datetime.fromtimestamp(
            os.path.getmtime(self.file)
        )

    def get_filename_datec(self):
        if self.filename_datec is None:
            self.calculate_filename_datec()
        
        return self.filename_datec

    def calculate_filename_datec(self):
        self.filename_datec = None

        filename_len = len(self.filename)

        try:
            # format: IMG20231229232507
            self.filename_datec = datetime.datetime.strptime(
                self.filename, '%%%%Y%m%d%H%M%S' + (
                    # 3, IMG|VID
                    # 14, 20231229232507
                    '%' * (filename_len - 3 - 14)
                )
            )
        except:
            pass
        
        if self.filename_datec is None:
            try:
                # format: IMG_20231229_232507
                self.filename_datec = datetime.datetime.strptime(
                    self.filename, '%%%%%Y%m%d%%H%M%S' + (
                        # 3, IMG|VID
                        # 2, _
                        # 14, 20231229232507
                        '%' * (filename_len - 3 - 2 - 14)
                    )
                )
            except:
                pass

def archive_file(sync_arch_file, archive_target_folder, archive_date, move_files=True, dry_run=False):
    def create_dir_if_not_exists(path):
        if not os.path.exists(path):
            if dry_run:
                print('>>> os.mkdir(%s)' % path)
            else:
                os.mkdir(path)

    create_dir_if_not_exists(archive_target_folder)

    archive_target_folder = os.path.join(archive_target_folder, archive_date.strftime('%Y'))
    create_dir_if_not_exists(archive_target_folder)

    archive_target_folder = os.path.join(archive_target_folder, archive_date.strftime('%m'))
    create_dir_if_not_exists(archive_target_folder)

    archive_target_file = os.path.join(archive_target_folder, sync_arch_file.get_filename())

    # * Si no existe un archivo en el directorio objetivo
    #    * Lo archivamos (moviendo o copiando segun el valor de move_files)
    if not os.path.exists(archive_target_file):
        if move_files:
            if dry_run:
                print('>>> shutil.move(%s, %s)' % (sync_arch_file.get_file(), archive_target_folder))
            else:
                shutil.move(sync_arch_file.get_file(), archive_target_folder)
        else:
            if dry_run:
                print('>>> shutil.copy(%s, %s)' % (sync_arch_file.get_file(), archive_target_folder))
            else:
                shutil.copy(sync_arch_file.get_file(), archive_target_folder)
    else:
        # * Si existe un archivo en el directorio objetivo con el mismo nombre
        # * Notificaremos el suceso
        print("WARNING: Collision on archive_file, file '%s' already exists." % archive_target_file)

        # * Si el sha1 de ambos archivos son identicos y si move_files=True borraremos el original
        if move_files:
            target_sync_arch_file = SyncArchFile(archive_target_file)
            if target_sync_arch_file.get_sha1() == sync_arch_file.get_sha1():
                if dry_run:
                    print('>>> os.remove(%s)' % sync_arch_file.get_file())
                else:
                    os.remove(sync_arch_file.get_file())
            else:
                print("ERROR: Collision on archive_file '%s', file '%s' already exists with diferent sha1 hash." % (sync_arch_file.get_file(), archive_target_file))
                return False

    return True

def archive_all(source_folder, target_folder, move_files=True, dry_run=True):
    if not os.path.exists(source_folder):
        print("ERROR: Directory '%s' not exists" % [source_folder])
        return False
    
    if not os.path.exists(target_folder):
        print("ERROR: Directory '%s' not exists" % [target_folder])
        return False

    for dirpath, dirs, files in os.walk(source_folder):
        trace_verbose("     + source: %s" % dirpath)
        
        for dir in dirs:
            archive_all(
                source_folder=os.path.join(dirpath, dir), 
                target_folder=target_folder, 
                move_files=move_files
            )

        for file in files:
            trace_verbose("       * file: %s" % file)
            
            sync_arch_file = SyncArchFile(file=os.path.join(dirpath, file))

            archive_target_folder = target_folder
            archive_date = sync_arch_file.get_meta_datec()

            if not archive_date is None:
                trace_verbose("         - exif date: %s" % archive_date)

            if archive_date is None:
                archive_date = sync_arch_file.get_filename_datec()
                if not archive_date is None:
                    trace_verbose("         - filename date: %s" % archive_date)
            

            if archive_date is None:
                archive_date = sync_arch_file.get_file_datec()
                archive_target_folder = os.path.join(target_folder, 'unclasified')

                if not archive_date is None:
                    trace_verbose("         - `unclasified` file creation date: %s" % archive_date)
            
            if not archive_file(
                sync_arch_file=sync_arch_file, 
                archive_target_folder=archive_target_folder, 
                archive_date=archive_date,
                move_files=move_files,
                dry_run=dry_run
            ):
                return False

def trace_verbose(text):
    if __debug__:
        print(text)