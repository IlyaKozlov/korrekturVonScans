import logging
import os
from typing import List, Dict

import pytesseract


class LanguageInstaller:

    def __init__(self) -> None:
        self.name2packages: Dict[str, List[str]] = {
            "rus": ["rus"],
            "srp+srp_latn": ["srp", "srp_latn"],
            "srp+srp_latn+rus+eng": ["srp", "srp_latn", "rus", "eng"]
        }
        self.name2script = {
            "rus": "apt install -y tesseract-ocr-rus",
            "srp+srp_latn": "apt install -y tesseract-ocr-srp tesseract-ocr-srp-latn",
            "srp+srp_latn+rus+eng": "apt install -y tesseract-ocr-srp tesseract-ocr-srp-latn tesseract-ocr-rus",
        }

    def install_language(self, name: str) -> None:
        if name not in self.name2packages:
            logging.warning(f"Can't find language {name}")
            return
        target_packages = set(self.name2packages.get(name))
        if len(target_packages - set(self._get_languages_list())) > 0:
            self._install(name)

    def _get_languages_list(self) -> List[str]:
        return pytesseract.get_languages()

    def _install(self, name: str) -> None:
        script = self.name2script.get(name)
        if script:
            os.system(script)
