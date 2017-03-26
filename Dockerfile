FROM python:3.5

ARG ppath
ARG fixturepath

ADD ./ /opt/code/
WORKDIR /opt/code/

# Install django-machina
RUN make install

# Install project's requirements
RUN pip install -r $ppath/requirements-dev.txt

# Setup project
RUN rm -rf $ppath/public/media/*
RUN rm -rf $ppath/public/static/*
RUN rm -rf $ppath/test.db
RUN python $ppath/manage.py migrate
RUN python $ppath/manage.py createsuperuser --username=admin --email=test@example.com --noinput
RUN python $ppath/manage.py loaddata $fixturepath/*
