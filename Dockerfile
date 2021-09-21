FROM python:3.8-slim-buster as build

# don't let pip give red-herrings about it being an old version
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update -qq && rm -rf /var/cache/*

RUN python3 -m venv /pyenv

COPY requirements.txt requirements.txt

RUN /pyenv/bin/pip install -r /requirements.txt

FROM python:3.8-slim-buster

COPY --from=build /pyenv /pyenv

WORKDIR /

COPY app.py /

CMD ["/pyenv/bin/python", "app.py"]
