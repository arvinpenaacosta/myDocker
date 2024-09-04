Sept 4. 2024

# APPLICATION STRUCURE
\APP_MSSQL
│ 
docker-compose.yml
docker-compose2.yml
│ 
├───database
│       docker-compose.yml
│       Dockerfile
│
└───frontend
    │   .env
    │   Dockerfile
    │   main.py
    │   requirements.txt
    │
    ├───certs
    │       server.crt
    │       server.key
    │       server_unencrypted.key
    │
    ├───statics
    │   └───assets
    │       ├───css
    │       │       style.css
    │       └───js
    │               script.js
    │
    ├───templates
    │       index.html

[RUN]
docker-compose -f docker-compose2.yml up

## SETUP CONFIGURATION ##
-------------------------
# Create desired Database and Tables according to the application
# for this project 
  Database : "devappDB"
  Table : "entries"

CREATE DATABASE devappDB;
USE devappDB;
CREATE TABLE entries (
        id INT IDENTITY(1,1) PRIMARY KEY,
        field1 NVARCHAR(255) NOT NULL,
        field2 NVARCHAR(255) NOT NULL
    );

-------------
.env
# DB_USER=sa
# DB_PASSWORD=Admin@123.
# DB_NAME=devappDB
# DB_HOST=localhost






