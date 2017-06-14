#!/bin/bash
# Reset the database and dependencies to those on master

git checkout master
sudo -u postgres dropdb manchester_traffic_offences && sudo -u postgres createdb manchester_traffic_offences

./vagrant/update.sh
