FROM python:3.9-slim-buster

RUN mkdir /var/bot
WORKDIR /var/bot

RUN pip install python_twitter discord.py
RUN mkdir logs

ENTRYPOINT [ "sh", "main.sh" ]
# ENTRYPOINT [ "bash" ]