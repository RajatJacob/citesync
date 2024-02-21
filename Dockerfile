FROM python:3.10-alpine

WORKDIR /app

COPY . .

RUN rm -f -R /app/chroma
RUN rm -f -R /app/papers

VOLUME /app/chroma
VOLUME /app/papers

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python3", "-m", "flask", "run", "--host", "0.0.0.0" ]