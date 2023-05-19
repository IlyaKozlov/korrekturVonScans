FROM z

RUN apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8
RUN locale-gen ru_RU.UTF-8
ENV LANG ru_RU.utf8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8
ENV TZ=Europe/Podgorica
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV PYTHONPATH /korrectur/
RUN apt update && apt install -y python3.10 python3-pip  libjpeg-dev libtesseract-dev libleptonica-dev tesseract-ocr-rus \
    tesseract-ocr python3-pil  python-poppler poppler-utils djvulibre-bin libexempi3 pngquant git autotools-dev automake libtool
#RUN git clone https://github.com/agl/jbig2enc && cd jbig2enc && ./autogen.sh && ./configure && make && make install


ADD requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
ADD resources /resources
ADD korrectur /korrectur

CMD ["python3", "/korrectur/api/app.py"]
