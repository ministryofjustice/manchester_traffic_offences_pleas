#!/bin/bash
rm -f /home/vagrant/.ssh/known_hosts
ssh-keyscan -t rsa,dsa -H github.com >> /home/vagrant/.ssh/known_hosts

sudo apt-get clean
sudo apt-get update
sudo apt-get upgrade -y
cd /pleas/
sudo ./apt/production.sh
sudo ./apt/development.sh
sudo ./apt/testing.sh
sudo easy_install pip
sudo pip install virtualenvwrapper

cd /home/vagrant/
mkdir -p .envs


grep -q '# make a plea startup' .bashrc || cat << EOF >> .bashrc
# make a plea startup
export WORKON_HOME=/home/vagrant/.envs
source /usr/local/bin/virtualenvwrapper.sh
workon manchester
echo -e "\\n\\n\\033[0;31mRun: ./manage.py runserver 0.0.0.0:8000\\033[0m\\n\\n"
EOF

echo "Setting VE wrapper"
WORKON_HOME=/home/vagrant/.envs
source /usr/local/bin/virtualenvwrapper.sh

echo "Setting up postgres"
sudo cp /pleas/vagrant/pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
sudo service postgresql restart
sudo -u postgres bash -c "psql postgres -tAc 'SELECT 1 FROM pg_roles WHERE rolname='\''jenkins'\' | grep -q 1 || createuser --superuser jenkins"

echo "Making the VE"
mkvirtualenv manchester
setvirtualenvproject $VIRTUAL_ENV /pleas/
workon manchester

pip install -r requirements/dev.txt
pip install -r requirements/testing.txt

sudo -u postgres createdb manchester_traffic_offences
./manage.py syncdb --noinput
./manage.py migrate --noinput
./manage.py compilemessages

set -x
sudo ln -s /usr/bin/nodejs /usr/bin/node
npm install
sudo npm install -g gulp-cli
