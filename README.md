# web-scraper
This web scraper scrapes a website, collects information about companies, stores the collected data in the database, and sends an automated email whenever new companies are listed in the site.

System requirement
----------------------
- Python
- Selenium
- Pyodbc
- Database driver (in the code I am using Microsoft Server driver)

To run the program use the following command
------------------------------------------------
python main.py -R <receiver's email address> -N <Server's Name> -S <sender's gmail address> 
-P <app generated password>

- R - receiver's email address(any domain)
- N - database server name
- S - sender's gmail address. Email is send using gmail SMTP server. Use gmail email addres ONLY.
- P - Google doesn't allow to use account password in a less secured application. Use app generated password from your google account.

T-SQL Script to create database and table
----------------------------------------------------
CREATE DATABASE asic_companies
ON (NAME = 'asic_companies_data',
     FILENAME = 'C:\SQL\asic_companies.mdf',
     SIZE = 10MB,
     MAXSIZE = 100MB,
     FILEGROWTH = 10%)
LOG ON (NAME = 'asic_companies_log',
     FILENAME = 'C:\SQL\asic_companies.ldf',
     SIZE = 5MB,
     MAXSIZE = 50MB,
     FILEGROWTH = 5%);
Go

Note: Here the assumption is that ‘'C:\SQL\’ file path exists in your local machine. If not create a folder ‘SQL’ under the C drive. If you want to change the file path modify the ‘FILENAME’ to reflect the correct file path name.

USE asic_companies
GO

CREATE TABLE companies_in_liquidation(
        company_number VARCHAR(20) PRIMARY KEY,
        company_name VARCHAR(255) NOT NULL,
notice_date DATE NOT NULL);
GO  
