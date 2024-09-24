import unittest
import os
import subprocess
import sys

from tests.SampleFiles import SampleFiles

import unclasified_archiver

class TestUnclasifiedArchiver(unittest.TestCase):
    def setUp(self):
        self.sample_files = SampleFiles()

        self.root_tests_dir = os.path.join(
            "test-files", "tests"
        )
        unclasified_archiver.create_dir_if_not_exists( self.root_tests_dir )
        

    def tearDown(self):
        # TODO: Borrar todos los archivos?
        pass

    def test1(self):
        base_dir = os.path.join(
            self.root_tests_dir, "test1"
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
            if os.path.exists(test_dir):
                print("ERROR: '%s' directory already exists." % test_dir)
                sys.exit(2)

            unclasified_archiver.create_dir_if_not_exists( test_dir )

            if not os.path.exists(test_dir):
                print("ERROR: '%s' directory was not created." % test_dir)
                sys.exit(2)

        unclasified_archiver.COPY_STATUS_DIR = status_folder

        self.assertEqual(
            unclasified_archiver.COPY_STATUS_DIR, status_folder
        )

        subprocess.call(["rsync", "-qa", self.sample_files.root_dir, target_folder])

        # unclasified_archiver.archive_all(
        #     source_folder=source_folder, 
        #     target_folder=target_folder,
        #     move_files=True,
        #     delete_empty_dir=False,
        #     ignore_no_media_files=False,
        #     force_add2status=False,
        #     dry_run=True
        # )

        # TODO: Comprobar que en archive estan los archivos en los directorios y con 
        # los nombres que se esperan

        # TODO: Comprobar que en unclasified no estan los archivos pero si las carpetas

        # TODO: Comprobar que se mueven archivos que sean no media

        # TODO: Comprobar que en status estan todos los archivos copiados

    # def test2(self):
    #     unclasified_archiver.COPY_STATUS_DIR = "test-files/user1_02/"

    #     unclasified_archiver.archive_all(
    #         source_folder="test-files/user1_02/unclasified", 
    #         target_folder="test-files/user1_02/archive",
    #         move_files=False,
    #         delete_empty_dir=False,
    #         ignore_no_media_files=False,
    #         force_add2status=False,
    #     )
