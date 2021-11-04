import os.path
from typing import Optional, Iterable

from PyPDF2 import PdfFileMerger
from PIL.Image import Image
from pdf2image import convert_from_path
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import resolve1

import pytesseract


class PdfHandler:

    def handle(self, path: str, lang: str = "eng+rus") -> str:
        total = self._get_page_num(path)
        base_name = os.path.basename(path).split('.')[0]
        dir_name = os.path.dirname(path)
        images_path = []
        for image_num, image in enumerate(self._get_images(path, total)):
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
