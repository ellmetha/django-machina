FROM python:3.5

ARG ppath

ADD ./ /opt/code/
WORKDIR /opt/code/

# Install nodejs, npm and lessc
RUN curl -sL https://deb.nodesource.com/setup_5.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g less

# Install django-machina
RUN make install

# Install project's requirements
RUN pip install -r $ppath/requirements.txt

# Setup project
RUN rm -rf $ppath/public/media/*
RUN rm -rf $ppath/public/static/*
RUN rm -rf $ppath/example.db
RUN python $ppath/src/manage.py migrate
RUN python $ppath/src/manage.py createsuperuser --username=admin --email=test@example.com --noinput
RUN python $ppath/src/manage.py loaddata $ppath/src/fixtures/*
