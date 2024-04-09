FROM python:latest

RUN pip install twitchio

ENTRYPOINT ["python", "/mnt/app/run.py"]
