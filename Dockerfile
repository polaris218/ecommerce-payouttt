FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
EXPOSE 8000
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
COPY . /code/
ENV STRIPE_SECRET_KEY=7!wg%_&mmsf44+x1d0&e7#k_!zv+z+e6l(o)v4p+v57$l7(lh&
ENV STRIPE_PUBLISHABLE_KEY=xvf
ENV PLAID_CLIENT_ID=asd
ENV PLAID_PUBLIC_KEY=asdf
ENV PLAID_SECRET=asdf
ENV PLAID_DEVELOPMENT_SECRET=asdf
ENV PLAID_ENVIRONMENT=Development
ENV SHIPPO_API_KEY=payTest

CMD python3 manage.py migrate
CMD python3 manage.py runserver 0.0.0.0:8000
