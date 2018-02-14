# SEMA2 Web Server Django

## Project Summary:

SEMA (Smartphone Ecological Momentary Assessment) is a suite of software for designing and conducting smartphone-based survey research. SEMA v2 involves administering a survey several times per day (at random times) over several days. However, SEMA2 can also be used to administer surveys less frequently (e.g., once daily, as in daily diary studies), or on an ad hoc basis (i.e., participants launch the survey manually at any time). Following extensive testing of the initial version of SEMA in 2013-2014, SEMA2 was developed in 2015 by researchers at Australian Catholic University and Orygen-The National Centre of Excellence in Youth Mental Health, in collaboration with a private software developer, Boosted Human. SEMA2 includes a multitude of features that enable researchers to easily and intuitively create and administer smartphone surveys and easily access and analyse collected data.


## Authors:

Harrison, A., Harrsion, S., Koval, P., Gleeson, J., Alvarez, M. (2017). SEMA: Smartphone Ecological Momentary Assessment (Version 2). [Computer software]. https://github.com/eorygen

## Project hosting page:

https://github.com/eorygen/sema2_web

Alternatively, users who do not have git installed on their machine may download it by clicking on Clone or download button, click on Download ZIP. Note an uncompress tool is required to extract the project files from the ZIP file.


## Issue Tracker:

https://github.com/eorygen/sema2_web/issues


## Forum & Mailing List:

https://groups.google.com/forum/#!forum/sema-surveys


## Documentation:

https://github.com/eorygen/sema2_web/wiki


## Requirements:

*   An Ubuntu virtual machine (for deployment) - https://www.digitalocean.com
*   A valid Apple App ID e.g. com.foocorp.sematest (for configuring push notifications)
*   A valid iOS production push notification .pem file (for configuring push notifications)
*   A Google GCM push key (for configuring push notifications on Android)
*   A free Mailgun account for sending email - https://www.mailgun.com
*   (optional) A free OpBeat account (for error tracking) - https://opbeat.com


Hello and welcome to the SEMA README. This document outlines how to install and run the open source deployment of SEMA
onto an Ubuntu server for testing purposes.

The examples below use a Digital Ocean $5 Droplet as the deployment server although this can be replaced with any Ubuntu
server of your choosing (AWS, local machine, etc).

Please see the individual SEMA iOS and Android app repositories for info on building & deploying the SEMA mobile apps
for your project.


## Creating a VM with Vagrant

You can easily test the SEMA server using the Vagrant system.

1.  Install Vagrant (https://www.vagrantup.com/docs/installation/)
2.  Clone the SEMA repo to your local machine
3.  Open the 'vagrant' directory in the repository
4.  Type 'vagrant up' to start the virtual machine
5.  Type 'vagrant ssh' once the machine has loaded to ssh into the VM
6.  Once in cd to the '/vagrant_data/deploy' directory
7.  Update your packages by running 'sudo apt-get update'
8.  Install ansible by running 'sudo apt-get install ansible' (make sure you install Ansible 2.0+
    - you may need to add the ansible PPA)
9.  You should now be able to execute the commands from the 'Provisioning' subsection of the 'DEPLOY SEMA' section below


## Creating a VM on Digital Ocean


You need to provision a droplet (in this case a linux VM running Ubuntu). To create a Droplet follow the instructions
below. After the droplet has been provisioned take note of the assigned IP address as it will be used in a later step.

https://www.digitalocean.com/community/tutorials/how-to-create-your-first-digitalocean-droplet-virtual-server

After setup:

1.  Install ansible by running 'sudo apt-get install ansible' (make sure you install Ansible 2.0+
    - you may need to add the ansible PPA)


## Set up MailGun

SEMA uses Mailgun to send invite emails. These instructions will use the default sandbox domain available to all Mailgun
users.

1.  Sign into your Mailgun account
2.  Click on 'Domains'
3.  Click on the sandbox domain in the list
4.  You will see a list of Domain Information. Take note of the values for 'API Key' and the domain for use in the env
    file later

MAILGUN_ACCESS_KEY = <API_KEY>
MAILGUN_SERVER_NAME = <DOMAIN>


## Deploy SEMA

The easiest way to get started with SEMA is to provision your server using the included Ansible script.

# Setup

1.  SSH into your droplet and clone the SEMA repo to somewhere in your home directory.
2.  Edit the 'app_vars.yml' file in the 'deploy' directory and fill out the values.
3.  Edit the 'env.production' file and fill out the values

# Provisioning

4.  Open the 'provision.yml' file in the deploy directory and have a look to see what it does. If you do not understand
    what this script will do to your server please view the Ansible docs here for more info: http://docs.ansible.com/

5.  cd into the 'deploy' directory and type:

    'ansible-playbook provision.yml -i hosts -K -v'

    to provision the server

6.  When prompted type your sudo password for your current user
7.  When prompted enter local or prod to choose the type of NGINX config you wish to use. The local config does not have
    HTTPS support. The Prod config forces HTTPS support and requires you to install SSL certificates into the
    <projectdir>/ssl directory. See the nginx_prod.conf.j2 config in th 'conf' directory for more info on where nginx
    expects to find the certificates.

    - SEMA will be installed and set up
    - If any issues arise check that your user has sufficient permissions to write to the installation directory

9.  The SEMA server should now be running and accessible via NGINX on your droplet IP

10. After making any changes to the env file you will need to restart uwsgi and nginx on your server.


## Install the iOS Push Certificates

1.  In order for IOS push notifications to work you will need to copy a valid IOS push notification certificate in PEM
    format into the <projectdir>/certs directory. The certificate should be named: 'production_push_cert.pem'
2.  For Google push notifications you will need to acquire a GCM push token and put it in your env file

    NOTE: These files and tokens must match those used in the apps you are deploying.


## Manual Provisioning

To manually provision a server and set up SEMA you should open the 'provision.yml' file in the 'deploy' directory and
have a look at what it does. You will need to replicate those steps.


## Toubleshooting

*   Most issues arise due to incorrect permissions - check that your deploy user and git repository users have the correct
    permissions

*   Check the UWSGI, NGINX and SEMA logs (SEMA logs are in <projectdir/logs>) to see why SEMA is crashing or unavailable.

