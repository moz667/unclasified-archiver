#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime, os, re, shelve, shutil, stat

import exifread
import ffmpeg
from pymediainfo import MediaInfo
from simple_file_checksum import get_checksum

MINIMAL_DATE = datetime.datetime(2000, 1, 1)
MAXIMAL_DATE = datetime.datetime.today()
COPY_STATUS_DIR = '/tmp' if not 'COPY_STATUS_DIR' in os.environ or not os.environ['COPY_STATUS_DIR'] else os.environ['COPY_STATUS_DIR']

class UncArchFile:
    TYPE_IMAGE = 'Image'
    TYPE_VIDEO = 'Video'
    TYPE_AUDIO = 'Audio'
    TYPE_OTHER = 'Other'

    TRASHED_FILE_PATTERN = r"^\.trashed-[0-9]+-"
    
    def __init__(self, file):
        self.file = file
        self.filename = os.path.basename(file)
        
        self.size = None
        self.file_type = None
        self.checksum = None

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

        media_info = None
        try:
            media_info = MediaInfo.parse(self.file)
        except Exception as e:
            # Caso especial dentro de .Sync dir de `Resilio Sync`
            if self.filename == 'root_acl_entry':
                f = trace_verbose
            else:
                f = print

            f("ERROR: Error on MediaInfo.parse('%s')" % self.get_file())
            f(repr(e))

        if media_info:
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
        if self.checksum is None:
            self.checksum = get_checksum(self.file)
        
        return self.checksum
    
    def get_meta_datec(self):
        if self.meta_datec is None:
            self.calculate_meta_datec()
        
        return self.meta_datec

    def calculate_meta_datec(self):
        self.meta_datec = None

        try:
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
                str_datetime = None
                f = open(self.file, 'rb')

                tags = exifread.process_file(f)

                if 'EXIF DateTimeOriginal' in tags:
                    str_datetime = tags['EXIF DateTimeOriginal'].__str__()
                
                if not str_datetime is None:
                    self.meta_datec = datetime.datetime.strptime(
                        str_datetime, '%Y:%m:%d %H:%M:%S'
                    )
        except:
            trace_verbose("ERROR: On calculate_meta_datec of '%s'." % self.file)

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
        #         Screenshot_2012-11-26-10-31-14.png
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

                    if not self.filename_datec:
                        self.filename_datec = self.format_str_as_date(
                            date_on_name[:10], '%Y-%m-%d'
                        )
                
                if self.filename_datec:
                    break

        if not self.filename_datec:
            # format: 20140104_161338
            self.filename_datec = self.format_str_as_date(
                self.filename[:8], '%Y%m%d'
            )

        if not self.filename_datec:
            # format: 2012-08-02 08.55.16
            self.filename_datec = self.format_str_as_date(
                self.filename[:10], '%Y-%m-%d'
            )

    def is_trashed_file(self):
        return re.match(self.TRASHED_FILE_PATTERN, self.filename) != None

    def get_clean_trashed_filename(self):
        return re.sub(self.TRASHED_FILE_PATTERN, "", self.filename)

    def format_str_as_date(self, str, format):
        global MAXIMAL_DATE, MINIMAL_DATE

        try:
            datetime_return = datetime.datetime.strptime(
                str, format
            )

            if datetime_return <= MAXIMAL_DATE and datetime_return >= MINIMAL_DATE:
                return datetime_return
            else:       
                trace_verbose(
                    "Date '%s' extracted from the string '%s' is greater than '%s' or is less than '%s'." % 
                    (
                        datetime_return.strftime('%Y-%m-%d %H:%M:%S'), 
                        str, 
                        MAXIMAL_DATE.strftime('%Y-%m-%d %H:%M:%S'), 
                        MINIMAL_DATE.strftime('%Y-%m-%d %H:%M:%S'), 
                    )
                )
                return None
        except:
            # trace_verbose("ERROR: On string '%s' when format as '%s'." % (str, format))
            return None
    
    def get_size(self):
        if self.size == None:
            self.size = os.path.getsize(self.file)
        return self.size

    def get_status_key(self):
        return "%s_%s" % (self.get_checksum(), self.get_size())

    def is_already_copied(self):
        d = shelve.open(os.path.join(COPY_STATUS_DIR, 'copy_status.shelve'))
        if self.get_status_key() in d:
            d.close()
            return True
        
        return False
    
    def set_already_copied(self):
        d = shelve.open(os.path.join(COPY_STATUS_DIR, 'copy_status.shelve'), writeback=True)
        d[self.get_status_key()] = True
        d.close()


def create_dir_if_not_exists(path, dry_run=False):
    if not os.path.exists(path):
        if dry_run:
            print('>>> os.mkdir(%s)' % path)
        else:
            os.mkdir(path)

# @var un_arch_file UncArchFile
def archive_file(unc_arch_file: UncArchFile, archive_target_folder, archive_date, move_files=True, force_add2status=False, dry_run=False):
    create_dir_if_not_exists(archive_target_folder, dry_run=dry_run)

    archive_target_folder = os.path.join(archive_target_folder, archive_date.strftime('%Y'))
    create_dir_if_not_exists(archive_target_folder, dry_run=dry_run)

    archive_target_folder = os.path.join(archive_target_folder, archive_date.strftime('%m'))
    create_dir_if_not_exists(archive_target_folder, dry_run=dry_run)

    archive_target_file = os.path.join(archive_target_folder, unc_arch_file.get_filename())

    # Caso especial: archivos borrados en android, por ejemplo:
    # .trashed-1703430355-IMG20231123161529_BURST000_COVER.jpg
    if unc_arch_file.is_trashed_file():
        archive_target_file = os.path.join(archive_target_folder, unc_arch_file.get_clean_trashed_filename())

    # * Si no existe un archivo en el directorio objetivo
    #    * Lo archivamos (moviendo o copiando segun el valor de move_files)
    if not os.path.exists(archive_target_file):
        if move_files:
            if dry_run:
                print('>>> shutil.move(%s, %s)' % (unc_arch_file.get_file(), archive_target_file))
            else:
                shutil.move(unc_arch_file.get_file(), archive_target_file)
        else:
            if dry_run:
                print(">>> if not unc_arch_file.is_already_copied():")
                print('>>>     shutil.copy(%s, %s)' % (unc_arch_file.get_file(), archive_target_file))
                print(">>>     unc_arch_file.set_already_copied()")
            else:
                if not unc_arch_file.is_already_copied():
                    shutil.copy(unc_arch_file.get_file(), archive_target_file)
                    unc_arch_file.set_already_copied()
                else:
                    trace_verbose("         - Already copied.")
    else:
        # * Si existe un archivo en el directorio objetivo con el mismo nombre
        # * Notificaremos el suceso
        trace_verbose("         - File '%s' already exists." % archive_target_file)

        target_unc_arch_file = UncArchFile(archive_target_file)
        
        # * Si el checksum de ambos archivos son identicos y si move_files=True borraremos el original
        if target_unc_arch_file.get_checksum() == unc_arch_file.get_checksum():
            if move_files:
                if dry_run:
                    print('>>> os.remove(%s)' % unc_arch_file.get_file())
                else:
                    os.remove(unc_arch_file.get_file())
            elif force_add2status and not unc_arch_file.is_already_copied():
                unc_arch_file.set_already_copied()
                trace_verbose("         - Added FORCED to copy_status.")
        else:
            print("ERROR: Collision on archive_file '%s', file '%s' already exists with diferent checksum." % (unc_arch_file.get_file(), archive_target_file))
            return False

    return True

def archive_all(source_folder, target_folder, move_files=True, delete_empty_dir=False, ignore_no_media_files=False, force_add2status=False, dry_run=True):
    if not os.path.exists(source_folder):
        print("ERROR: Directory '%s' not exists" % [source_folder])
        return False
    
    if not os.path.exists(target_folder):
        print("ERROR: Directory '%s' not exists" % [target_folder])
        return False

    for dirpath, dirs, files in os.walk(source_folder):
        trace_verbose("     + source: %s" % dirpath)
        
        for file in files:
            trace_verbose("       * file: %s/%s" % (dirpath, file))
            
            unc_arch_file = UncArchFile(file=os.path.join(dirpath, file))

            if ignore_no_media_files and unc_arch_file.get_file_type() == UncArchFile.TYPE_OTHER:
                trace_verbose("         - Is ignore because is not a media file.")
                continue

            archive_target_folder = target_folder

            if not unc_arch_file.get_file_type() in [UncArchFile.TYPE_IMAGE, UncArchFile.TYPE_VIDEO]:
                archive_target_folder = os.path.join(target_folder, unc_arch_file.get_file_type().lower())
            
            archive_date = unc_arch_file.get_meta_datec()

            if archive_date:
                trace_verbose("         - exif date: %s" % archive_date)

            if archive_date is None:
                archive_date = unc_arch_file.get_filename_datec()
                if archive_date:
                    trace_verbose("         - filename date: %s" % archive_date)
            

            if archive_date is None:
                archive_date = unc_arch_file.get_file_datec()
                archive_target_folder = os.path.join(
                    target_folder, 
                    'modified-date'
                )

                create_dir_if_not_exists(archive_target_folder, dry_run=dry_run)

                archive_target_folder = os.path.join(archive_target_folder, unc_arch_file.get_file_type().lower())

                if not archive_date is None:
                    trace_verbose("         - `modified-date` file modification date: %s" % archive_date)

            if not archive_file(
                unc_arch_file=unc_arch_file, 
                archive_target_folder=archive_target_folder, 
                archive_date=archive_date,
                move_files=move_files,
                force_add2status=force_add2status,
                dry_run=dry_run
            ):
                trace_verbose("         - Can't archive file")
    
    if delete_empty_dir:
        rm_empty_dirs_recursive(source_folder=source_folder, dry_run=dry_run)

def rm_empty_dirs_recursive(source_folder, preserve=True, dry_run=True):
    for path in (os.path.join(source_folder, p) for p in os.listdir(source_folder)):
        st = os.stat(path)
        if stat.S_ISDIR(st.st_mode):
            rm_empty_dirs_recursive(path, preserve=False, dry_run=dry_run)
    
    if not preserve and len(os.listdir(source_folder)) == 0:
        try:
            if dry_run:
                print(">>> os.rmdir('%s')" % source_folder)
            else:
                os.rmdir(source_folder)
        except IOError:
            print("Error: IOError trying to delete '%s'" % source_folder)

def trace_verbose(text):
    if __debug__:
        print(text)