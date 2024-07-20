FROM python:3.9
ENV PYTHONBUFFERED=1
WORKDIR /application

RUN apt-get update --yes --quiet \
  && apt-get install -y build-essential curl \
  && curl -sL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs --no-install-recommends \
  && apt-get install -y ffmpeg

COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install setuptools~=57.5.0
RUN python3 -m pip install -r requirements.txt
COPY . .
RUN python3 manage.py collectstatic --no-input
CMD ["python3", "manage.py", "migrate"]
