import unittest
import subprocess
import os
import sys

import unclasified_archiver

class TestUnclasifiedArchiver(unittest.TestCase):
    def setUp(self):
        # TODO: Comprobar que existen archivos en el origen pero no en el objetivo?
        # if not os.path.exists("test-files2"):
        #     print("Hay que crear los archivos de ejemplo antes ejecutando el script: generate-tests-samples.sh")
        #     sys.exit(2)
        pass

    def tearDown(self):
        # TODO: Borrar todos los archivos?
        pass

    def test1(self):
        unclasified_archiver.COPY_STATUS_DIR = "test-files/user1_01/"

        unclasified_archiver.archive_all(
            source_folder="test-files/user1_01/unclasified", 
            target_folder="test-files/user1_01/archive",
            move_files=False,
            delete_empty_dir=False,
            ignore_no_media_files=False,
            force_add2status=False,
        )

        # TODO: Comprobar que en archive estan los archivos en los directorios y con 
        # los nombres que se esperan

        # TODO: Comprobar que en unclasified estan los archivos (no se han movido)

        # TODO: Comprobar que se mueven archivos que sean no media

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

if __name__ == '__main__':
    unittest.main()

#         # Crear archivos temporales para imágenes (jpg y png) y videos (mp4)
#         self.image1 = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
#         self.image2 = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
#         self.video1 = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
#         self.video2 = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)

#         # Escribimos contenido binario simulado para imágenes y videos
#         self.image1.write(b"\xff\xd8\xff\xe0\x00\x10JFIF")  # Cabecera JPEG simulada
#         self.image2.write(b"\xff\xd8\xff\xe0\x00\x10JFIF")  # Cabecera JPEG simulada
#         self.video1.write(b"\x00\x00\x00\x18ftypmp42")  # Cabecera MP4 simulada
#         self.video2.write(b"\x00\x00\x00\x18ftypmp42")  # Cabecera MP4 simulada

#         # Reiniciamos el puntero de los archivos
#         self.image1.seek(0)
#         self.image2.seek(0)
#         self.video1.seek(0)
#         self.video2.seek(0)

#     def tearDown(self):
#         # Eliminar los archivos temporales después de cada prueba
#         os.remove(self.image1.name)
#         os.remove(self.image2.name)
#         os.remove(self.video1.name)
#         os.remove(self.video2.name)

#     def test_calcular_checksum_imagen(self):
#         # Validar checksum de imágenes idénticas
#         checksum_img1 = calcular_checksum(self.image1.name)
#         checksum_img2 = calcular_checksum(self.image2.name)
#         self.assertEqual(checksum_img1, checksum_img2)

#     def test_calcular_checksum_video(self):
#         # Validar checksum de videos idénticos
#         checksum_vid1 = calcular_checksum(self.video1.name)
#         checksum_vid2 = calcular_checksum(self.video2.name)
#         self.assertEqual(checksum_vid1, checksum_vid2)

#     def test_validar_checksum_imagen(self):
#         # Validar que la comparación de checksums de imágenes funciona
#         self.assertTrue(validar_checksum(self.image1.name, self.image2.name))

#     def test_validar_checksum_video(self):
#         # Validar que la comparación de checksums de videos funciona
#         self.assertTrue(validar_checksum(self.video1.name, self.video2.name))

#     def test_mover_archivo_imagen(self):
#         # Validar que la imagen se mueve correctamente
#         dest_path = self.image1.name + "_moved.jpg"
#         self.assertTrue(mover_archivo(self.image1.name, dest_path))
#         self.assertTrue(os.path.exists(dest_path))
#         os.remove(dest_path)  # Limpiar

#     def test_mover_archivo_video(self):
#         # Validar que el video se mueve correctamente
#         dest_path = self.video1.name + "_moved.mp4"
#         self.assertTrue(mover_archivo(self.video1.name, dest_path))
#         self.assertTrue(os.path.exists(dest_path))
#         os.remove(dest_path)  # Limpiar

# if __name__ == '__main__':
#     unittest.main()
