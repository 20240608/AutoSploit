FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-dev \
    git \
    postgresql-client \
    apache2 && \
    rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN git clone https://github.com/20240608/AutoSploit.git /AutoSploit
WORKDIR /AutoSploit

RUN pip install -r requirements.txt

EXPOSE 80 443 4444

CMD ["/entrypoint.sh"]

