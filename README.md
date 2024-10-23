git config --global core.autocrlf input



git config --global core.autocrlf input

# Update your package list
sudo apt update

# Install MongoDB
sudo apt install -y mongodb

# Start the MongoDB service
sudo service mongodb start

mongod --version

sudo service mongodb start
sudo service mongodb status




# postgres (>= 13.0)
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
sudo -u postgres psql


# update postgres
sudo service postgresql stop
sudo apt remove postgresql postgresql-contrib
sudo apt autoremove
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install postgresql-13 postgresql-contrib
sudo service postgresql start

sudo -u postgres psql

# create a new database (you can name it anything you want, e.g., mydatabase):
CREATE DATABASE mydatabase;
# CREATE USER myuser WITH PASSWORD 'mypassword';
CREATE USER myuser WITH PASSWORD 'mypassword';
# Grant privileges to the user on the database:
GRANT ALL PRIVILEGES ON DATABASE mydatabase TO myuser;
# TO EXIT
\q



sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
sudo service postgresql status
sudo service postgresql stop
sudo service postgresql restart

sudo visudo
# User privilege specification
root    ALL=(ALL:ALL) ALL

codespace ALL=(ALL) NOPASSWD:ALL
sudo service postgresql status
