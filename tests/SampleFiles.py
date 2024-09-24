import os
import sys

from simple_file_checksum import get_checksum

# source: https://stackoverflow.com/questions/6760685/what-is-the-best-way-of-implementing-singleton-in-python
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SampleFiles(metaclass=Singleton):
    def __init__(self) -> None:
        self.root_dir = "test-files/samples"
        self.dates=(
            '2024-09-01 08:00:00',
            '2024-08-01 08:00:00',
            '2024-07-01 08:00:00',
            '2024-06-01 08:00:00',
            '2024-05-01 08:00:00',
            '2024-04-01 08:00:00',
            '2024-03-01 08:00:00',
            '2024-02-01 08:00:00',
            '2024-01-01 08:00:00',
            '2023-12-01 08:00:00',
        )
        
        self.files = {}
        self.populate_files()

        self.checksums = {}
        self.populate_checksums()


    def populate_files(self):
        base_files = []

        for i in range(1, 11):
            base_files.append('image-%s.jpg' % f"{i:02}")
            base_files.append('video-%s.mp4' % f"{i:02}")

        self.files = {
            '01-base': base_files, 
            '02-base-diferent-checksum': base_files, 
            '03-base-clone': base_files, 
            '04-trashed-files': [
                '.trashed-0000000001-image-01.jpg', 
                '.trashed-0000000001-video-01.mp4', 
                '.trashed-0000000002-image-02.jpg', 
                '.trashed-0000000002-video-02.mp4', 
                '.trashed-0000000003-image-03.jpg', 
                '.trashed-0000000003-video-03.mp4', 
                '.trashed-0000000004-image-04.jpg', 
                '.trashed-0000000004-video-04.mp4', 
                '.trashed-0000000005-image-05.jpg', 
                '.trashed-0000000005-video-05.mp4', 
                '.trashed-0000000006-image-06.jpg', 
                '.trashed-0000000006-video-06.mp4', 
                '.trashed-0000000007-image-07.jpg', 
                '.trashed-0000000007-video-07.mp4', 
                '.trashed-0000000008-image-08.jpg', 
                '.trashed-0000000008-video-08.mp4', 
                '.trashed-0000000009-image-09.jpg', 
                '.trashed-0000000009-video-09.mp4', 
                '.trashed-0000000010-image-10.jpg', 
                '.trashed-0000000010-video-10.mp4', 
            ], 
            '05-no-exif-with-names': [
                '2013-12-29-23-25-07_photo.jpg', 
                '2013-12-29-23-25-07_video.mp4', 
                'ALTER_2023-12-29-23-25-07.jpg', 
                'ALTER_20231229-232507.jpg', 
                'ALTER_20231229_232507.jpg', 
                'ALTER_20231229232507.jpg', 
                'ALTER_2023-12-29-23-25-07.mp4', 
                'ALTER_20231229-232507.mp4', 
                'ALTER_20231229_232507.mp4', 
                'ALTER_20231229232507.mp4', 
                'ALTER_20231229-WA0002.jpg', 
                'ALTER_20231229-WA0002.mp4', 
                'IMG_20231229_232507.jpg', 
                'IMG20231229232507.jpg', 
                'VID_20231229_232507.mp4', 
                'VID20231229232507.mp4', 
            ], 
            '06-no-exif-modified-file-date': base_files, 
            '07-no-media': [
                'text-01.txt', 
                'text-02.txt', 
                'text-03.txt', 
                'text-04.txt', 
                'text-05.txt', 
                'text-06.txt', 
                'text-07.txt', 
                'text-08.txt', 
                'text-09.txt', 
                'text-10.txt', 
            ], 
        }

    def populate_checksums(self):
        self.checksums = {}

        for sample_dir in self.files:
            cur_dir_checksums = {}
            for file in self.files[sample_dir]:
                cur_fullpath_file = os.path.join(
                    self.root_dir, sample_dir, file
                )
                cur_dir_checksums[file] = get_checksum(cur_fullpath_file)

            self.checksums[sample_dir] = cur_dir_checksums
