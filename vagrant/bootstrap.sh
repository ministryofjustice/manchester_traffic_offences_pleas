#!/bin/bash
rm -f /home/vagrant/.ssh/known_hosts
ssh-keyscan -t rsa,dsa -H github.com >> /home/vagrant/.ssh/known_hosts

sudo add-apt-repository ppa:chris-lea/node.js
sudo apt-get update
sudo apt-get upgrade
sudo apt-get -y install git postgresql postgresql-contrib postgresql-server-dev-9.3 build-essential python-dev libxml2-dev libxslt-dev python-setuptools nodejs ruby-sass libfontconfig redis-server libssl-dev libffi-dev
sudo apt-get -y install build-dep python-psycopg2
sudo apt-get -y install unoconv default-jre
sudo easy_install pip
sudo pip install virtualenvwrapper

cd /home/vagrant/
mkdir -p .envs

sed -i '$a\
\
export WORKON_HOME=/home/vagrant/.envs\
source /usr/local/bin/virtualenvwrapper.sh\
workon manchester\
echo -e "\\n\\n\\033[0;31mRun: ./manage.py runserver 0.0.0.0:8000\\033[0m\\n\\n"\
' .bashrc

echo "Setting VE wrapper"
WORKON_HOME=/home/vagrant/.envs
source /usr/local/bin/virtualenvwrapper.sh

echo "Setting up postgres"
sudo cp /pleas/vagrant/pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
sudo service postgresql restart

echo "Making the VE"
mkvirtualenv manchester
setvirtualenvproject $VIRTUAL_ENV /pleas/
workon manchester

pip install -r requirements/dev.txt

sudo -u postgres createdb manchester_traffic_offences
./manage.py syncdb --noinput
./manage.py migrate --noinput

sudo npm install -g npm
npm install
sudo npm install -g gulp-cli
