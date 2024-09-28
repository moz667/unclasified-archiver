from datetime import datetime
import unittest
import os
import subprocess
import sys

from simple_file_checksum import get_checksum

import unclasified_archiver

from SampleFiles import SampleFiles


class TestUnclasifiedArchiver(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.sample_files = SampleFiles()
        self.root_tests_dir = os.path.join(
            "test-files", "tests"
        )

        # Check sample files
        for sample_dir in self.sample_files.files:
            for file in self.sample_files.files[sample_dir]:
                cur_fullpath_file = os.path.join(
                    self.sample_files.root_dir, sample_dir, file
                )
                if not os.path.exists(cur_fullpath_file):
                    print("ERROR: No existen los archivos de ejemplo, ejecute 'generate-tests-samples.sh' para generarlos")
                    sys.exit(2)

        unclasified_archiver.create_dir_if_not_exists( self.root_tests_dir )

        if os.listdir(self.root_tests_dir):
            print("ERROR: El directorio '%s' no esta vacio." % self.root_tests_dir)
            sys.exit(2)
        

    # TODO: Maybe delete all tests files?
    # def tearDown(self):
    #     pass

    def create_testdirs(self, test_base_dirname):
        base_dir = os.path.join(
            self.root_tests_dir, test_base_dirname
        )

        source_folder = os.path.join(
           base_dir, "unclasified"
        )

        target_folder = os.path.join(
           base_dir, "archive"
        )

        status_folder = os.path.join(
           base_dir, "copy_status"
        )

        for test_dir in (base_dir, source_folder, target_folder, status_folder):
            unclasified_archiver.create_dir_if_not_exists( test_dir )

            if not os.path.exists(test_dir):
                print("ERROR: '%s' directory was not created." % test_dir)
                sys.exit(2)
        
        return (source_folder, target_folder, status_folder)

    def test_archive_all_default_args(self):
        (source_folder, target_folder, status_folder) = self.create_testdirs(
            "archive_all"
        )

        unclasified_archiver.COPY_STATUS_DIR = status_folder

        self.assertEqual(
            unclasified_archiver.COPY_STATUS_DIR, status_folder
        )

        subprocess.call([
            "rsync", "-qa", 
            self.sample_files.root_dir + os.path.sep, 
            source_folder + os.path.sep
        ])

        unclasified_archiver.archive_all(
            source_folder=source_folder, 
            target_folder=target_folder,
            move_files=True,
            delete_empty_dir=False,
            ignore_no_media_files=False,
            force_add2status=False,
            dry_run=False
        )

        # Al mover (move_files=True) no generamos copy_status
        self.assertFalse(os.listdir(status_folder))

        # Chequear directorios en target_folder
        self.check_create_target_dirs(target_folder)
        
        # Comprobar que en archive estan los archivos en los directorios y con 
        # los nombres que se esperan
        self.check_target_files(target_folder)

        # Comprobar que en unclasified no estan los archivos pero si las carpetas
        for sample_dir in self.sample_files.files:
            source_sample_dir = os.path.join(source_folder, sample_dir)
            self.assertTrue(
                os.path.exists(source_sample_dir), 
                "ERROR: Se ha borrado el directorio '%s'" % source_sample_dir
            )
            self.assertFalse(
                os.listdir(source_sample_dir), 
                "ERROR: Archivos encontrados en '%s'" % source_sample_dir
            )

    def test_archive_all_copy(self):
        (source_folder, target_folder, status_folder) = self.create_testdirs(
            "archive_all_copy"
        )

        unclasified_archiver.COPY_STATUS_DIR = status_folder

        self.assertEqual(
            unclasified_archiver.COPY_STATUS_DIR, status_folder
        )

        subprocess.call([
            "rsync", "-qa", 
            self.sample_files.root_dir + os.path.sep, 
            source_folder + os.path.sep
        ])

        unclasified_archiver.archive_all(
            source_folder=source_folder, 
            target_folder=target_folder,
            move_files=False,
            delete_empty_dir=False,
            ignore_no_media_files=False,
            force_add2status=False,
            dry_run=False
        )

        # Al copiar (move_files=False) generamos copy_status
        self.assertTrue(os.listdir(status_folder))

        # Chequear directorios en target_folder
        self.check_create_target_dirs(target_folder)
        
        # Comprobar que en archive estan los archivos en los directorios y con 
        # los nombres que se esperan
        self.check_target_files(target_folder)

        # Comprobar que en unclasified no estan los archivos pero si las carpetas
        for sample_dir in self.sample_files.files:
            source_sample_dir = os.path.join(source_folder, sample_dir)
            self.assertTrue(
                os.path.exists(source_sample_dir), 
                "ERROR: Se ha borrado el directorio '%s'" % source_sample_dir
            )
            self.assertTrue(
                os.listdir(source_sample_dir), 
                "ERROR: Archivos NO encontrados en '%s'" % source_sample_dir
            )


    def test_archive_all_resilio_backup(self):
        (source_folder, target_folder, status_folder) = self.create_testdirs(
            "archive_all_resilio_backup"
        )

        unclasified_archiver.COPY_STATUS_DIR = status_folder

        self.assertEqual(
            unclasified_archiver.COPY_STATUS_DIR, status_folder
        )

        subprocess.call([
            "rsync", "-qa", 
            self.sample_files.root_dir + os.path.sep, 
            source_folder + os.path.sep
        ])

        unclasified_archiver.archive_all(
            source_folder=source_folder, 
            target_folder=target_folder,
            move_files=False,
            delete_empty_dir=False,
            ignore_no_media_files=True,
            force_add2status=False,
            dry_run=False
        )

        # Al copiar (move_files=False) generamos copy_status
        self.assertTrue(os.listdir(status_folder))

        # Chequear directorios en target_folder
        self.check_create_target_dirs(target_folder, check_no_media_files=False)
        
        # Comprobar que en archive estan los archivos en los directorios y con 
        # los nombres que se esperan
        self.check_target_files(target_folder)

        # Comprobar que en unclasified no estan los archivos pero si las carpetas
        for sample_dir in self.sample_files.files:
            source_sample_dir = os.path.join(source_folder, sample_dir)
            self.assertTrue(
                os.path.exists(source_sample_dir), 
                "ERROR: Se ha borrado el directorio '%s'" % source_sample_dir
            )
            self.assertTrue(
                os.listdir(source_sample_dir), 
                "ERROR: Archivos NO encontrados en '%s'" % source_sample_dir
            )

    def check_create_target_dirs(self, target_folder, check_no_media_files=True):
        cur_target_modified_date = os.path.join(
            target_folder, 'modified-date'
        )

        self.assertTrue(os.path.exists(cur_target_modified_date))

        i = 1

        for d in self.sample_files.dates:
            cur_datetime = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
            
            self.assertTrue(os.path.exists(os.path.join(
                target_folder, 
                cur_datetime.strftime('%Y'), cur_datetime.strftime('%m')
            )))

            for file_type in ("image", "video"):
                cur_archive_dir = os.path.join(
                    cur_target_modified_date, file_type, 
                    cur_datetime.strftime('%Y'), cur_datetime.strftime('%m')
                )
                self.assertTrue(
                    os.path.exists(cur_archive_dir),
                    "ERROR: No existe el directorio '%s'" % cur_archive_dir
                )

            # Comprobar que se trataron o NO, los NO-MEDIA
            cur_nomedia_file = os.path.join(
                cur_target_modified_date, "other", 
                cur_datetime.strftime('%Y'), cur_datetime.strftime('%m'),
                "text-%s.txt" % f"{i:02}"
            )

            if check_no_media_files:
                self.assertTrue(
                    os.path.exists(cur_nomedia_file),
                    "ERROR: No existe el archivo no-media '%s'" % cur_nomedia_file
                )
            else:
                self.assertFalse(
                    os.path.exists(cur_nomedia_file),
                    "ERROR: Existe el archivo no-media '%s'" % cur_nomedia_file
                )

            i += 1
        
        # Caso especial: 2013-12-29-23-25-07_photo.(jpg|mp4)
        cur_archive_dir = os.path.join(
            target_folder, '2013', '12'
        )
        self.assertTrue(
            os.path.exists(cur_archive_dir),
            "ERROR: No existe el directorio '%s'" % cur_archive_dir
        )
    
    def check_target_files(self, target_folder):

        # 1) Archivos base y colisiones
        # archive/year/month/(image|video)-[01...10].(jpg|mp4)
        # archive/year/month/(image|video)-[01...10] (Collision <checksum1>).(jpg|mp4)
        # archive/year/month/(image|video)-[01...10] (Collision <checksum2>).(jpg|mp4)
        file_index = 1

        for d in self.sample_files.dates:
            cur_datetime = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
            cur_archive_dir = os.path.join(
                target_folder, 
                cur_datetime.strftime('%Y'), cur_datetime.strftime('%m')
            )

            for pattern in ("image-%s.jpg", "video-%s.mp4"):
                cur_filename = pattern % f"{file_index:02}"
                cur_file = os.path.join(cur_archive_dir, cur_filename)
                cur_file_exists = os.path.exists(cur_file)
                
                self.assertTrue(
                    cur_file_exists,
                    "ERROR: No existe el archivo '%s'" % cur_file
                )

                if cur_file_exists:
                    self.assertEqual(
                        self.sample_files.checksums["01-base"][cur_filename],
                        get_checksum(cur_file),
                        "ERROR: '%s' no es el archivo que esperabamos ya que no se trata de '%s' de 06-no-exif-modified-file-date"
                    )

                collision_pattern = pattern % (
                    f"{file_index:02}" + " (Collision %s)"
                )

                collision_filename = collision_pattern % (
                    self.sample_files.checksums["02-base-diferent-checksum"][cur_filename]
                )
                collision_file = os.path.join(cur_archive_dir, collision_filename)
                self.assertTrue(
                    os.path.exists(collision_file),
                    "ERROR: No existe el archivo '%s'" % collision_file
                )

                collision_filename = collision_pattern % (
                    self.sample_files.checksums["04-trashed-files"][
                        ".trashed-00000000%s-%s" % (f"{file_index:02}", cur_filename)
                    ]
                )
                collision_file = os.path.join(cur_archive_dir, collision_filename)
                self.assertTrue(
                    os.path.exists(collision_file),
                    "ERROR: No existe el archivo '%s'" % collision_file
                )
            
            file_index += 1

        # 1) Archivos sin exif clasificados por nombre: (05-no-exif-with-names)
        # Todos se deberian almacenar en archive/2023/12/ menos los dos primeros:
        # * 2013-12-29-23-25-07_photo.jpg
        # * 2013-12-29-23-25-07_video.mp4
        for i in range(len(self.sample_files.files["05-no-exif-with-names"])):
            cur_archive_dir = os.path.join(
                target_folder, 
                "2023" if i > 1 else "2013", 
                "12"
            )
            cur_filename = self.sample_files.files["05-no-exif-with-names"][i]
            cur_file = os.path.join(cur_archive_dir, cur_filename)

            self.assertTrue(
                os.path.exists(cur_file),
                "ERROR: No existe el archivo '%s'" % cur_file
            )

if __name__ == '__main__':
    unittest.main()