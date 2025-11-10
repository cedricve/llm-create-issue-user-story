FROM python:3.13.5-bullseye

RUN apt-get update && \
    apt-get -y install jq && \
    rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /action/entrypoint.sh
COPY create_issue_user_story.py /action/create_issue_user_story.py
COPY requirements.txt /action/requirements.txt

RUN pip3 install -r /action/requirements.txt && \
    chmod +x /action/entrypoint.sh && \
    chmod +x /action/create_issue_user_story.py

ENTRYPOINT ["/action/entrypoint.sh"]
