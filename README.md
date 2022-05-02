# Basic-University-Registration-System
Basic University Registration System

Project is written with Python, Django and MySQL.
Assumed you unzipped and you are reading READ.ME in the project folder.


Requirements: You should create a virtual environment for this project. 

We will be giving a tutorial for conda environment.

1) conda env create --name MyEnv python=3.8
2) conda activate MyEnv
3) conda install -c anaconda django
4) conda install -c anaconda mysql-connector-python
5) conda install -c conda-forge mysqlclient

NOTE: Be careful about that your default python is the environment's python.

You need to download MySql and install it on your computer.



Steps to run:

1)After installing MySql on your computer, open MySql workbench and log in 
as root user, 
then run the following query:
"""
CREATE USER 'haruntaha'@'localhost' IDENTIFIED BY 'haruntaha';
GRANT ALL PRIVILEGES ON * . * TO 'haruntaha'@'localhost';
ALTER USER 'haruntaha'@'localhost' IDENTIFIED WITH mysql_native_password BY 'haruntaha';

CREATE DATABASE  IF NOT EXISTS `university_registration_system`;
USE `university_registration_system`;
"""

2)In terminal run: cd universityregistrationsystem/regist
3)In terminal run: python3 create_db.py
4)In terminal run: cd ..
5)In terminal run: python3 manage.py runserver
