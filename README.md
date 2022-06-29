<p align="center">
  <img src="bin/static/logoComplete.svg"/>
</p>

# Multi-Purpose Software License Manager

The Multi-Purpose Software License Manager (SLM, for short) is a web application that is meant to facilitate the management of software distribution.

## Table of Contents

1. Introduction
2. Getting Started
3. Documentation\
   3.1 Directory Structure\
   3.2 Database\
   3.3 API
4. Helping out

## Intruduction

SLM was initially developed as part of the Captsone Project for the Bachelors of Informatic Engineering of the University of Porto. Taking place as a piece of work for BUILT-CoLAB, the project became open-source and is open for improvements and commercial use as per the terms of the MIT License agreement. 

SLM is a Web Application whose main purpose is to help license distributors to manage their existing products, customers and licenses alike. Nowadays, the extreme complexity of the market and the need to reduce the frequency of piracy requires a concise tool that is clear, objective and straightforward. This project was created as a solution to these issues by using a more user-friendly interface that allows for the management of important data features and to observe statistics that are important from a marketing point of view.

The implementation of the web application uses the Flask microframework, in Python 3.9.  As a distributor you do not need to do anything other than following the first section of this introductory file. However, as a developer, you are free to check out this entire file in order to learn how to customize / improve the features that SLM offers.

The application has a rich interface and allows license distributors to add as many Products and License Keys as they wish. These same License Keys can be edited, deleted or even disabled. All these modifications are also saved in a Changelog to prevent misuse and allow managers and customer support agents to keep track of what happens to each License. For security reasons, the Changelogs are irremovable and the actions of local administrators will always be registered into the log storage. Apart from these features, administrators can also create Customers, store their contact information or even remove them from the service should they ever request that.

As it stands, the SLM aims to offer the essential features of any common License Managing software while keeping its Multi-Purpose nature and carrying a unique GUI.


## Getting Started

In order to get everything ready you are required to have Docker installed. After doing that, and cloning the project from this repository, you should simply follow the following steps:

**Step 1:** Build the docker image

```
docker build --tag license-manager .
```

**Step 2:** Run it with the command

Linux (Bash):

```bash
docker run -v $(pwd)/bin/sqlite.db:/license-manager/bin/sqlite.db -p 8000:8000 license-manager
```

Windows (Powershell):

```powershell
docker run -v ${PWD}/bin/sqlite.db:/license-manager/bin/sqlite.db -p 8000:8000 license-manager
```

Optional docker envs: `--env WORKERS=2 --env THREADS=4 --env PORT=8000`

After doing these steps, the project should be available at `http://localhost:8000/`.

**Step 3:** To stop the image from running simply run

```
docker stop $(docker ps -q --filter ancestor=license-manager )
```

##### How to log into the Dashboard

By default, the login data is defined as:

```
Username: root
Password: root
```

In order to change these login details, you will need to modify the .env variable, by changing the `ADMINUSERNAME` and `ADMINPASSWORD` fields, respectively.

## Documentation

This section is meant to help developers and contributors to modify, customize and augment this project in any way that is suitable for them.

#### a) Directory Structure

As mentioned in previously, the Project uses FLASK, a micro web framework that is written in Python. All the necessary contents are stored in the `bin` folder.

In a more graphical way, the directory structure is represented bellow, with some comments to help you out.

```
.
└── bin
    └── static                                                    # All static resources go here
        ├── bootstrap.bundle.min.js                               # Bootstrap's Javascript Module
        ├── bootstrap.min.css                                     # Bootstrap's Styling Module
        ├── loginImage.svg                                        # Login Image used for the main page
        └── style.css                                             # The overall styling of the Project
    └── templates                                                 # Generally, all pages (.html files) should go here!
        ├── base.html                                             # The basic template that is available in every page
        ├── cpanel.html                                           # CPanel's main page
        ├── index.html                                            # This is the login page
        ├── keydata.html                                          # This is the page that displays the information of each key
        ├── product.html                                          # This is the page that displays the information of each product (and its keys)
        └── profile.html                                          # The user profile
    ├── __init__.py                                               # This is the initiating file for FLASK. You shouldn't need to modify it ...
    ├── auth.py                                                   # All routes (API Endpoints) related to authentication should go here.
    ├── databaseAPI.py                                            # All functions required to communicate with the Database go here.
    ├── keys.py                                                   # All data related to key management should come here.
    ├── main.py                                                   # All routes (API Endpoints) related to anything (except authentication) should go here.
    ├── models.py                                                 # This files is meant for SQLAlchemy, used by FLASK to interact with our SQLite database.
    └── sqlite.db                                                 # This file is our SQLite database.

└── client
    └── clientTest.py                                             # This file simulates the Client-Side application trying to validate with our app.

└── docs
    └── .............                                             # All data inside this folder is merely done for evaluation purposes under pedagogical terms. It is not used in the Project.

├── .env                                                          # Environment Variables file. Do not delete it.
├── .gitignore                                                    # Used to ignore certain cache files from Python.
├── README.md                                                     # This documentation.
└── requirements.txt                                              # Used for Step 1. After the set-up it may not be necessary anymore if you are not planning to use in other machines.
```

#### b) Database

The database used in SLM is the SQLite database. The file is present right in the first level of the `bin` directory. It is automatically generated by the application if the file does not yet exist. Note, however, that this only occurs once every time you run the application. Deleting the file while the web app is running will effectively render the entire application useless until you restart it.

Also, be aware that when you delete this file, ALL data will be lost. This includes (but is not limited to): User accounts, Products, Licenses, Registered Devices, Customers and even the Changelog. Doing so, will reset the entire project as if you were opening it for the first time. We suggest you to create a routine that generates a backup every now and then in order to prevent the loss of critical data. 

When it comes to the documentation of the database, you can check its structure in the `models.py` file. However, in order to help you get through the SQLAlchemy's syntax, we will represent the same information in the file in a tabular format:

| USER Table | Type | PK  | UQ  | AI  |
| ---------- | ---- | --- | --- | --- |
| id         | INT  | X   |     | X   |
| email      | TEXT |     | X   |     |
| password   | TEXT |     |     |     |
| name   | TEXT |     | X   |     |
| owner   | BOOL |     |    |     |
| disabled   | BOOL |     |    |     |
| timestamp  | INT |     |   |     |

| PRODUCT Table | Type | PK  | UQ  | AI  |
| ------------- | ---- | --- | --- | --- |
| id            | INT  | X   |     | X   |
| name          | TEXT |     | X   |     |
| category          | TEXT |     |    |     |
| image          | TEXT |     |     |     |
| details          | TEXT |     |     |     |
| privateK      | TEXT |     | X   |     |
| publicK       | TEXT |     | X   |     |
| apiK          | TEXT |     | X   |     |

| CLIENT Table  | Type | PK  | UQ  | AI  |
| ------------- | ---- | --- | --- | --- |
| id            | INT  | X   |     | X   |
| name  | TEXT |     |     |     |
| email | TEXT |     |     |     |
| phone | TEXT |     |     |     |
| country | TEXT |     |     |     |
| registrydate    | INT  |     |     |     |

| KEY Table     | Type | PK  | UQ  | AI  |
| ------------- | ---- | --- | --- | --- |
| id            | INT  | X   |     | X   |
| productid     | INT  | FK  |     |     |
| clientid      | INT  | FK  |     |     |
| serialkey     | TEXT |     | X   |     |
| maxdevices    | INT  |     |     |     |
| devices       | INT  |     |     |     |
| status        | INT  |     |     |     |
| expirydate    | INT  |     |     |     |

| REGISTRATION Table | Type | PK  | UQ  | AI  |
| ------------------ | ---- | --- | --- | --- |
| id                 | INT  | X   |     | X   |
| keyid              | INT  | FK  |
| hardwareid         | TEXT |     |     |     |

| CHANGELOG Table | Type | PK  | UQ  | AI  |
| --------------- | ---- | --- | --- | --- |
| id              | INT  | X   |     | X   |
| keyid           | INT  | FK  |     |     |
| userid          | INT  | FK  |     |     |
| timestamp       | INT  |     |     |     |
| action          | TEXT |     |     |     |
| description          | TEXT |     |     |     |

All modifications in SQLAlchemy are based on this model. You are free to use another database, but you will need to change the Flask settings (`__init__.py` file).

In order to facilitate the transition between databases, the entire web app connects with the database by using the functions in the `databaseAPI.py` file. This means you are free to rewrite these functions, so long the inputs and returns continue to make sense in the context of the overall web app. In any case, the functions either return nothing or they simply return an object whose fields / local variables are identical to each field in the respective table. Some other functions may return specific values. You can see in the table bellow which functions return an object and which don't.

| Function name              | Return details                   |
| -------------------------- | -------------------------------- |
| generateUser()             | None                             |
| obtainUser()               | User object (1 record)           |
| createUser()               | None                             |
| changeUserPassword()       | None                             |
| toggleUserStatus()       	 | None                             |
| getProduct()               | Product object (0+ records)      |
| getDistinctClients()       | Integer                          |
| getProductByID             | Product object (1 record)        |
| createProduct()            | Product object (1 record)        |
| editProduct()              | None                             |
| getProductThroughAPI()     | Product object (1 record)        |
| getKeys()                  | Key object (0+ records)          |
| getKeysBySerialKey()       | Key object (1 record)            |
| createKey()                | ID field of new Key object       |
| setKeyState()              | None                             |
| deleteKey()                | None                             |
| resetKey()                 | None                             |
| getKeyData()               | Key object (1 record)            |
| getKeyStatistics()         | 2 Integers                       |
| getKeyAndClient()          | Key JOIN Customer object         |
| submitLog()                | None                             |
| getKeyLogs()               | Changelog object (0+ records)    |
| getUserLogs()              | Changelog object (0+ records)    |
| queryLogs()                | Changelog object (0+ records)    |
| queryValidationStats()     | 2 Integers                       |
| getRegistration()          | Registration object (1 record)   |
| getKeyHWIDs()              | Registration object (1+ records) |
| deleteRegistrationsOfKey() | None                             |
| deleteRegistrationOfHWID() | None                             |
| addRegistration()          | None                             |
| createCustomer()           | None                             |
| modifyCustomer()           | None                             |
| deleteCustomer()           | None                             |
| getCustomer()              | Customer object (0+ records)     |
| getCustomerByID()          | Customer object (1 record)       |

## Section 4 :: API Documentation

To be developed ...
