FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
EXPOSE 8000
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y nginx 
COPY app.conf /etc/nginx/conf.d/app.conf
COPY . /code/
EXPOSE 80
RUN rm -rf /etc/nginx/sites-enabled/default   
CMD python3 manage.py makemigrations && python3 manage.py migrate &&  python3 manage.py runserver 0.0.0.0:8000
