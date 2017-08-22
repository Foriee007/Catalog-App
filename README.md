# Linux-Server-Configuration-AWS-Web-App

## Project Description
This is the fifth project for Full Stack Web Developer Nanodegree Program on Udacity.

In this project, a distribution Linux on a virtual machine needs to be configurated to host web applications base on  project Item Catalog.

You can visit http://18.220.158.181 for the website deployed.

##  Walkthrough tasks
1. Launch your Virtual Machine on Amazon Web Services  http://amazonaws.com
2. Follow the instructions provided to SSH into your server
3. Create a new user named grader
4. Give the grader the permission to sudo
5. Update all currently installed packages
6. Change the SSH port from 22 to 2200
7. Configure the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123)
8. Configure the local timezone to UTC
9. Install and configure Apache to serve a Python mod_wsgi application
10. Install and configure PostgreSQL:
	- Do not allow remote connections
	- Create a new user named catalog that has limited permissions to your catalog application database
11. Install git, clone and setup your Catalog App project (from your GitHub repository from earlier in the Nanodegree program) so that it functions correctly when visiting your server’s IP address in a browser. Remember to set this up appropriately so that your .git directory is not publicly accessible via a browser!

## Launch Virtual Machine
1.This project uses Amazon Lightsail to create a Linux server instance
2.Start a new Ubuntu Linux server instance on Amazon Lightsail.
    ```
    Log in!
    Create an instance
    Choose an instance image: Ubuntu (OS only)
    Choose your instance plan (lowest tier is fine)
    Give your instance a hostname
    Wait for startup
    Once the instance has started up, follow the instructions provided to SSH into your server.
    ```

## Instructions for SSH access to the instance
1. Download Private Key below
2. Create an SSH key pair for grader using the ssh-keygen tool.
    ```
      ssh-keygen -t rsa

      To login
      
      ssh -i .ssh/grader_udacity grader@18.220.158.181 -p 2200
      ```

## Create a new user named grader
1. `sudo adduser grader`
2. `vim /etc/sudoers`
3. `touch /etc/sudoers.d/grader`
4. `vim /etc/sudoers.d/grader`, type in `grader ALL=(ALL:ALL) ALL`, save and quit

## Set ssh login using keys
1. generate keys on local machine using`ssh-keygen` ; then save the private key in `~/.ssh` on local machine
2. deploy public key on developement enviroment

	On you virtual machine:
	```
	$ su - grader
	$ mkdir .ssh
	$ touch .ssh/authorized_keys
	$ vim .ssh/authorized_keys
	```
	Copy the public key generated on your local machine to this file and save
	```
	$ chmod 700 .ssh
	$ chmod 644 .ssh/authorized_keys
	```

3. reload SSH using `service ssh restart`
4. now you can use ssh to login with the new user you created

	`ssh -i [privateKeyFilename] grader@18.220.158.181`

## Update all currently installed packages

	sudo apt-get update
	sudo apt-get upgrade

## Change the SSH port from 22 to 2200
1. Use `sudo vim /etc/ssh/sshd_config` and then change Port 22 to Port 2200 , save & quit.
2. Reload SSH using `sudo service ssh restart`

## Configure the Uncomplicated Firewall (UFW)

Configure the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123)

	sudo ufw allow 2200/tcp
	sudo ufw allow 80/tcp
	sudo ufw allow 123/udp
	sudo ufw enable

## Configure the local timezone to UTC
1. Configure the time zone `sudo dpkg-reconfigure tzdata`
2. It is already set to UTC.

## Install and configure Apache to serve a Python mod_wsgi application
1. Install Apache `sudo apt-get install apache2`
2. Install mod_wsgi `sudo apt-get install python-setuptools libapache2-mod-wsgi`
3. Restart Apache `sudo service apache2 restart`

## Install and configure PostgreSQL
1. Install PostgreSQL `sudo apt-get install postgresql`
2. Check if no remote connections are allowed `sudo vim /etc/postgresql/9.5/main/pg_hba.conf`
3. Login as user "postgres" `sudo su - postgres`
4. Get into postgreSQL shell `psql`
5. Create a new database named catalog  and create a new user named catalog in postgreSQL shell

	```
	postgres=# CREATE DATABASE catalog;
	postgres=# CREATE USER catalog;
	```
5. Set a password for user catalog

	```
	postgres=# ALTER ROLE catalog WITH PASSWORD 'catalog123';
	```
6. Give user "catalog" permission to "catalog" application database

	```
	postgres=# GRANT ALL PRIVILEGES ON DATABASE catalog TO catalog;
	```
7. Quit postgreSQL `postgres=# \q`
8. Exit from user "postgres"

	```
	exit
	```

## Install git, clone and setup your Catalog App project.
1. Install Git using `sudo apt-get install git`
2. Use `cd /var/www` to move to the /var/www directory
3. Create the application directory `sudo mkdir FlaskApp`
4. Move inside this directory using `cd FlaskApp`
5. Clone the Catalog App to the virtual machine `git clone https://github.com/Foriee007/Catalog-App.git`
6. Rename the project's name `sudo mv ./catalog_aws_app ./FlaskApp`
7. Move to the inner FlaskApp directory using `cd FlaskApp`
8. Install pip `sudo apt-get install python-pip`
9. Use pip to install dependencies
```
    sudo pip install
    sudo pip install flask
    sudo pip install httplib2
    sudo pip install oauth2client
    sudo pip install requests
    sudo pip install sqlalchemy
```

10. Install psycopg2 `sudo apt-get -qqy install postgresql python-psycopg2`
. Create database schema `sudo python database_setup.py`
. Run `sudo python loadmenuitems.py` to insert basic data

## Configure and Enable a New Virtual Host
1. Create FlaskApp.conf to edit: `sudo nano /etc/apache2/sites-available/FlaskApp.conf`
2. Add the following lines of code to the file to configure the virtual host.

	```
	<VirtualHost *:80>
		ServerName 18.220.158.181
		ServerAdmin admin@mywebsite.com
		WSGIScriptAlias / /var/www/FlaskApp/flaskapp.wsgi
		<Directory /var/www/FlaskApp/FlaskApp/>
			Order allow,deny
			Allow from all
		</Directory>
		Alias /static /var/www/FlaskApp/FlaskApp/static
		<Directory /var/www/FlaskApp/FlaskApp/static/>
			Order allow,deny
			Allow from all
		</Directory>
		ErrorLog ${APACHE_LOG_DIR}/error.log
		LogLevel warn
		CustomLog ${APACHE_LOG_DIR}/access.log combined
	</VirtualHost>
	```
3. Enable the virtual host with the following command: `sudo a2ensite FlaskApp`

## Create the .wsgi File
1. Create the .wsgi File under /var/www/FlaskApp:

	```
	cd /var/www/FlaskApp
	sudo nano flaskapp.wsgi
	```
2. Add the following lines of code to the flaskapp.wsgi file:

	```
	#!/usr/bin/python
	import sys
	import logging
	logging.basicConfig(stream=sys.stderr)
	sys.path.insert(0,"/var/www/FlaskApp/")

	from FlaskApp import app as application
	application.secret_key = 'Add your secret key'
	```

## Restart Apache
1. Restart Apache `sudo service apache2 restart `

## References:
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04
