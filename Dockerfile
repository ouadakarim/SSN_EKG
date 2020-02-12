FROM python:3.6
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
ENTRYPOINT python3 manage.py migrate \
        && python3 manage.py runserver 0.0.0.0:8000
