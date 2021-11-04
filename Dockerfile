FROM ubuntu:bionic-20210118

RUN apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8
RUN locale-gen ru_RU.UTF-8
ENV LANG ru_RU.utf8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8
ENV PYTHONPATH /korrectur/


RUN apt update && apt install -y python3 python3-pip  libjpeg-dev libtesseract-dev libleptonica-dev tesseract-ocr-rus \
    tesseract-ocr python3-pil  python-poppler poppler-utils
ADD requirements.txt .
ADD korrectur /korrectur
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
CMD ["python3", "/korrectur/api/app.py"]