FROM python:3.8.13-alpine3.16
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apk update && apk install libpq-dev gcc && apk install python3-psycopg2 && \
    pip3 install -r requirements.txt &&\
    apk install apt-transport-https ca-certificates curl && \
    curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" |  tee /etc/apt/sources.list.d/kubernetes.list && \
    apk update && \
    apk install kubectl
COPY . .
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

