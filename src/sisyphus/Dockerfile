FROM python:3.8.13-alpine3.16
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get -y install libpq-dev gcc && apt-get install -y python3-psycopg2 && \
    pip3 install -r requirements.txt &&\
    apt-get install -y apt-transport-https ca-certificates curl && \
    curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" |  tee /etc/apt/sources.list.d/kubernetes.list && \
    apt-get update && \
    apt-get install -y kubectl
COPY . .
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

