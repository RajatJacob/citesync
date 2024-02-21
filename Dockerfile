FROM python:3.10

WORKDIR /app

ADD ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

ADD . .

VOLUME /usr/local/lib/python3.10/site-packages
VOLUME /app/chroma
VOLUME /app/papers

EXPOSE 5000

ENTRYPOINT [ "python3", "-m", "flask", "run", "--host", "0.0.0.0" ]
