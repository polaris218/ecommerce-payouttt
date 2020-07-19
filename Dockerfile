FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
EXPOSE 8000
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
COPY . /code/
RUN python3 manage.py migrate
CMD python3 manage.py runserver 0.0.0.0:8000
