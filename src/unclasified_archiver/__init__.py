#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime, os, shutil

import exifread
from exif import Image
import ffmpeg
from pymediainfo import MediaInfo
import whatimage

from simple_file_checksum import get_checksum

MINIMAL_DATE = datetime.datetime(2000, 1, 1)
MAXIMAL_DATE = datetime.datetime.today()

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

    def get_checksum(self):
        self.sha1 = get_checksum(self.file)
    
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
        if not self.filename_datec:
            self.calculate_filename_datec()
            if not self.filename_datec:
                trace_verbose(
                    "Can't calculate date by filename on file '%s'." % 
                    self.filename
                )
        
        return self.filename_datec

    def calculate_filename_datec(self):
        self.filename_datec = None

        # format: IMG20231229232507
        # 3, IMG|VID
        # 14, 20231229232507
        self.filename_datec = self.format_str_as_date(
            self.filename[3:17], '%Y%m%d%H%M%S'
        )

        # format: IMG_20231229_232507
        # 4, IMG_|VID_
        # 15, 20231229_232507
        if not self.filename_datec:
            self.filename_datec = self.format_str_as_date(
                self.filename[4:19], '%Y%m%d_%H%M%S'
            )

        # format: 2013-03-17-19-57-16_photo
        #         2013-03-17-19-57-50_deco
        # 4, 2013-03-17-19-57-50
        if not self.filename_datec:
            self.filename_datec = self.format_str_as_date(
                self.filename[:19], '%Y-%m-%d-%H-%M-%S'
            )

        # format: _20140209_174329
        #         CYMERA_20130615_103530
        #         image_20161021_165225
        #         PANO_20130320_160358
        #         Pixlr_20160411150815984
        #         pixlr_20171021160935846
        #         Screenshot_20160629-213115
        #         TRIM_20131203_183531
        #         ???-20140320-WA0002.jpg
        # X, XXXX
        # 8, 20231229
        if not self.filename_datec:
            for separator in ('_', '-'):
                date_on_name = self.filename.split(separator, 1)
                if len(date_on_name) == 2:
                    date_on_name = date_on_name[1]
                    self.filename_datec = self.format_str_as_date(
                        date_on_name[:8], '%Y%m%d'
                    )
                
                if self.filename_datec:
                    break

        # Others...
        # IMG-20140320-WA0002.jpg
        # Screenshot_2015-04-28-07-07-54.png
        # Screenshot_2015-05-01-07-46-55~2.jpg
        # .trashed-1703430355-IMG20231123161529_BURST000_COVER.jpg


    def format_str_as_date(self, str, format):
        global MAXIMAL_DATE, MINIMAL_DATE

        try:
            # TODO: minimal year
            datetime_return = datetime.datetime.strptime(
                str, format
            )

            if datetime_return <= MAXIMAL_DATE and datetime_return >= MINIMAL_DATE:
                return datetime_return
            else:       
                trace_verbose(
                    "Date '%s' extracted from the string '%s' is greater than '%s' or is less than '%s'." % 
                    (
                        datetime_return.strftime('%Y%m%d_%H%M%S'), 
                        str, 
                        MAXIMAL_DATE.strftime('%Y%m%d_%H%M%S'),
                        MINIMAL_DATE.strftime('%Y%m%d_%H%M%S'),
                    )
                )
                return None
        except:
            return None


def create_dir_if_not_exists(path, dry_run=False):
    if not os.path.exists(path):
        if dry_run:
            print('>>> os.mkdir(%s)' % path)
        else:
            os.mkdir(path)

def archive_file(sync_arch_file, archive_target_folder, archive_date, move_files=True, dry_run=False):
    create_dir_if_not_exists(archive_target_folder, dry_run=dry_run)

    archive_target_folder = os.path.join(archive_target_folder, archive_date.strftime('%Y'))
    create_dir_if_not_exists(archive_target_folder, dry_run=dry_run)

    archive_target_folder = os.path.join(archive_target_folder, archive_date.strftime('%m'))
    create_dir_if_not_exists(archive_target_folder, dry_run=dry_run)

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
            if target_sync_arch_file.get_checksum() == sync_arch_file.get_checksum():
                if dry_run:
                    print('>>> os.remove(%s)' % sync_arch_file.get_file())
                else:
                    os.remove(sync_arch_file.get_file())
            else:
                print("ERROR: Collision on archive_file '%s', file '%s' already exists with diferent checksum." % (sync_arch_file.get_file(), archive_target_file))
                return False

    return True

def archive_all(source_folder, target_folder, move_files=True, delete_empty_dir=False, dry_run=True):
    if not os.path.exists(source_folder):
        print("ERROR: Directory '%s' not exists" % [source_folder])
        return False
    
    if not os.path.exists(target_folder):
        print("ERROR: Directory '%s' not exists" % [target_folder])
        return False

    for dirpath, dirs, files in os.walk(source_folder):
        trace_verbose("     + source: %s" % dirpath)
        
        for dir in dirs:
            cur_source_folder = os.path.join(dirpath, dir)
            
            archive_all(
                source_folder=cur_source_folder, 
                target_folder=target_folder, 
                move_files=move_files,
                delete_empty_dir=delete_empty_dir,
                dry_run=dry_run
            )

            if delete_empty_dir and len(os.listdir(cur_source_folder)) == 0:
                if dry_run:
                    print(">>> os.rmdir('%s')" % cur_source_folder)
                else:
                    os.rmdir(cur_source_folder)

        for file in files:
            trace_verbose("       * file: %s" % file)
            
            sync_arch_file = SyncArchFile(file=os.path.join(dirpath, file))

            archive_target_folder = os.path.join(target_folder, sync_arch_file.get_file_type().lower())
            archive_date = sync_arch_file.get_meta_datec()

            if archive_date:
                trace_verbose("         - exif date: %s" % archive_date)

            if archive_date is None:
                archive_date = sync_arch_file.get_filename_datec()
                if archive_date:
                    trace_verbose("         - filename date: %s" % archive_date)
            

            if archive_date is None:
                archive_date = sync_arch_file.get_file_datec()
                archive_target_folder = os.path.join(
                    target_folder, 
                    'unclasified'
                )

                create_dir_if_not_exists(archive_target_folder, dry_run=dry_run)

                archive_target_folder = os.path.join(archive_target_folder, sync_arch_file.get_file_type().lower())

                if not archive_date is None:
                    trace_verbose("         - `unclasified` file creation date: %s" % archive_date)

            if not archive_file(
                sync_arch_file=sync_arch_file, 
                archive_target_folder=archive_target_folder, 
                archive_date=archive_date,
                move_files=move_files,
                dry_run=dry_run
            ):
                print("WARNING: Can't archive file '%s'" % file)

def trace_verbose(text):
    if __debug__:
        print(text)