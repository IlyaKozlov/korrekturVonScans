import os.path
import subprocess
from typing import Optional, Iterable, List

from PyPDF2 import PdfFileMerger
from PIL.Image import Image
from pdf2image import convert_from_path
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1

import pytesseract
from pytesseract import get_languages

from errors.korrektur_base_exception import KorrekturConversionException


class PdfHandler:

    def __init__(self, timeout: int = 180) -> None:
        super().__init__()
        self.timeout = timeout

    def handle(self, path: str, lang: str = "eng+rus") -> str:
        print(f"lang {lang}")
        if path.endswith(".djvu"):
            path = self._convert(path)
        total = self._get_page_num(path)
        base_name = os.path.basename(path).split('.')[0]
        dir_name = os.path.dirname(path)
        images_path = []
        print(path)
        for image_num, image in enumerate(self._get_images(path, total)):
            x, y = image.size
            x = x // 3
            y = y // 3
            image = image.resize((x, y))
            pdf_path = os.path.join(dir_name, "{}_{:06d}.pdf".format(base_name, image_num))
            pdf = pytesseract.image_to_pdf_or_hocr(image, extension='pdf', lang=lang)
            with open(pdf_path, 'w+b') as f:
                f.write(pdf)  # pdf type is bytes by default
            images_path.append(pdf_path)

        merger = PdfFileMerger()
        for pdf in images_path:
            merger.append(pdf)

        path_out = os.path.join(dir_name, "result.pdf")
        merger.write(path_out)
        return path_out

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
        first_page = 1
        images = convert_from_path(pdf_path=path, first_page=first_page, last_page=first_page)
        while len(images) > 0:
            yield from images
            first_page += 1
            images = convert_from_path(pdf_path=path, first_page=first_page, last_page=first_page)
            print("Get pages from {:03d} to {:03d} from {}".format(first_page, first_page + 1, total))

    @staticmethod
    def get_languages() -> List[str]:
        return get_languages()
