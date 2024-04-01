FROM python:3.12.2-alpine3.19

WORKDIR /app

COPY birding_il_bots/requirements.txt birding_il_bots/requirements.txt

RUN pip install --no-cache-dir -r birding_il_bots/requirements.txt

COPY birding_il_bots/ birding_il_bots/

CMD [ "python", "-m", "birding_il_bots.main" ]
