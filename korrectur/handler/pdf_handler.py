import glob
import os.path
import shutil
import subprocess
import tempfile
from typing import Optional, Iterable, List

import img2pdf
import ocrmypdf
from PyPDF2 import PdfFileMerger, PdfFileWriter, PdfFileReader
from PyPDF2.pdf import PageObject
from tqdm import tqdm
import PIL
from PIL.Image import Image
from pdf2image import convert_from_path
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1

import pytesseract
from pytesseract import get_languages

from color_corrector.color_corrector import ColorCorrector
from errors.korrektur_base_exception import KorrekturConversionException


class PdfHandler:

    def __init__(self, timeout: int = 180) -> None:
        super().__init__()
        self.timeout = timeout
        self.color_corrector = ColorCorrector()


    def handle(self, path: str, tmpdir: str, lang: str = "eng+rus") -> str:
        print(f"lang {lang}")
        if path.endswith(".djvu"):
            path = self._convert(path)
        total = self._get_page_num(path)
        base_name = os.path.basename(path).split('.')[0]
        images_path = []

        for i, image in enumerate(tqdm(self._get_images(path), total=total)):
            image_corrected = self.color_corrector.handle_image(image)
            path_out = os.path.join(tmpdir, f"page_{i:04d}.jpg")
            image_corrected.save(path_out, quality=50)
            images_path.append(path_out)

        pdf_path_in = os.path.join(tmpdir, "name.pdf")
        pdf_path_out_part = os.path.join(tmpdir, f"{base_name}_part.pdf")
        pdf_path_out = os.path.join(tmpdir, f"{base_name}.pdf")

        with open(pdf_path_in, "wb") as file_out:
            file_out.write(img2pdf.convert(images_path))

        ocrmypdf.ocr(pdf_path_in, language=lang, output_file=pdf_path_out_part, optimize=3, deskew=False)
        shutil.move(pdf_path_out_part, pdf_path_out)
        return pdf_path_out

    def _convert(self, path: str) -> str:
        """
        convert file path and return path to the converted file
        :param path: path to source file
        :return: path to result file
        """
        if path.endswith(".pdf"):
            return path
        elif path.endswith("djvu"):
            path_out = path.replace(".djvu", ".pdf")
            command = ["ddjvu", "-format=pdf", "-quality=85", "-verbose", path, path_out]
            conversion_results = subprocess.run(command,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                timeout=self.timeout)
            error_message = conversion_results.stderr.decode().strip()
            if len(error_message) > 0:
                print(error_message)
            return path_out
        else:
            raise KorrekturConversionException(msg="cannot convert {}".format(os.path.basename(path)))

    def _get_page_num(self, path: str) -> int:
        try:
            with open(path, 'rb') as file:
                parser = PDFParser(file)
                document = PDFDocument(parser)
                return resolve1(document.catalog['Pages'])['Count']
        except:
            return 0

    def _get_images(self, path: str, total: Optional[int] = None) -> Iterable[Image]:
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = []
            first_page = 1
            images: List[Image] = convert_from_path(pdf_path=path, first_page=first_page, last_page=first_page)
            while len(images) > 0:
                for image in images:
                    path_out = "{}/{:04d}.webp".format(tmpdir, len(paths))
                    image.save(path_out)
                    paths.append(path_out)
                first_page += 1
                images = convert_from_path(pdf_path=path, first_page=first_page, last_page=first_page)
                print("Get pages from {:03d} to {:03d} from {}".format(first_page, first_page + 1, total))
            for image_path in tqdm(paths):
                yield PIL.Image.open(image_path)

    @staticmethod
    def get_languages() -> List[str]:
        return get_languages()
