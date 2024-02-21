FROM python:3.10

WORKDIR /app

COPY . .

VOLUME /app/chroma
VOLUME /app/papers

RUN pip install flask
RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python3", "-m", "flask", "run", "--host", "0.0.0.0" ]