# License Key Manager

[API Documentation](https://documenter.getpostman.com/view/20172540/UVsSP3vk)

## Section 1 :: Setting up the Project

**Step 1:** In the main directory of the repository, run the following command:

```
pip install -r requirements.txt
```

**Step 2:** While in the same directory as in the previous step, run the flask application using the following command:

Windows / Linux:
```
python3 -m flask run
```

The website will be available inside ```http://localhost:5000/```. 

The login data is:
```
Username: root
Password: root
```
(You can see how to these parameters by checking Section 3 of this document)

You do not need to set-up any environmental variables as the project now uses `python-dotenv` to load the `.env` file present in this repository. Without this file your application throw an error, forcing you to either reacquire this file or to manually set the environment variable `FLASK_APP=bin`.

## Section 2 :: Project Introduction

The License Key Manager is a web app that aims to facilitate the management of license keys by various license distributors. It uses the Flask micro web framework to maintain its RESTFUL API. As a distributor you do not need to do anything other than following the first section of this introductory file. As a developer, you are free to check out Section 3 in order to customize the features that this project currently offers.

Despite being visually simple, our web app allows license distributors to add as many Products and License Keys as they wish. These same Keys can be edited, deleted, modified. All these modifications are also saved in a Changelog to prevent misuse and allow managers and customer support agents to keep track of what's going on with the key.

## Section 3 :: Documentation

This section is meant to help owners of this app data to modify, customize and augment this project in any way that is suitable for them.

#### a) Directory Structure

As mentioned in Section 2, the Project uses FLASK, a micro web framework that is written in Python. All the necessary contents are stored in the `bin` folder.

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
    └── .............                                             # All data inside this folder is merely done for evaluation purposes under pedagogical terms.

├── .env                                                          # Environment Variables file. Do not delete it.
├── .gitignore                                                    # Used to ignore certain cache files from Python.
├── README.md                                                     # This documentation.
└── requirements.txt                                              # Used for Step 1. After the set-up it may not be necessary anymore if you are not planning to use in other machines.
```

#### b) Database

The database being used is the SQLite database. The file is present right in the first level of the `bin` directory. It is automatically generated by the application if the file does not yet exist. Note, however, that this only occurs once every time you run the application. Deleting the file while the web app is running will effectively render the entire application useless until you restart it. 

Be aware that when you delete this file, ALL data will be lost. This includes (but is not limited to): Login account, Products, Keys, Registered Devices, Doing so, will effectively reset the entire project as if you were opening it for the first time.

When it comes to the documentation of the database, you can check its structure in the `models.py` file. But, in order to help you get through the SQLAlchemy's syntax, we will represent the same information in the file in a tabular format:

| USER Table  | Type  | PK  | UQ | AI  |
|---|---|---|---|---|
| id | INT  | X |   | X  |
| email  | TEXT  |   | X  |   |
| password  | TEXT  |   |   |   |
| username  | TEXT  |   | X  |   |

| PRODUCT Table  | Type  | PK  | UQ | AI  |
|---|---|---|---|---|
| id | INT  | X |   | X  |
| name  | TEXT  |   | X  |   |
| logo  | TEXT  |   |   |   |
| privateK  | TEXT  |   | X  |   |
| publicK  | TEXT  |   | X  |   |
| apiK  | TEXT  |   | X  |   |

| KEY Table  | Type  | PK  | UQ | AI  |
|---|---|---|---|---|
| id | INT  | X |   | X  |
| productid  | INT  | FK  |
| customername  | TEXT  |   |   |   |
| customeremail  | TEXT  |   |   |   |
| customerphone  | TEXT  |   |   |   |
| serialkey  | TEXT  |   | X  |   |
| maxdevices  | INT  |   |   |   |
| devices  | INT  |   |   |   |
| status  | INT  |   |   |   |

| REGISTRATION Table  | Type  | PK  | UQ | AI  |
|---|---|---|---|---|
| id | INT  | X |   | X  |
| keyid  | INT  | FK  |
| hardwareid  | TEXT  |   |   |   |

| CHANGELOG Table  | Type  | PK  | UQ | AI  |
|---|---|---|---|---|
| id | INT  | X |   | X  |
| keyid  | INT  | FK  |
| timestamp  | INT  |   |   |   |
| action  | TEXT  |   |   |   |

All modifications in SQLAlchemy are based on this model. You are free to use another database, but you will need to change the Flask settings (`__init__.py` file). 

In order to facilitate the transition between databases, the entire web app connects with the database by using the functions in the `databaseAPI.py` file. This means you are free to rewrite these functions, so long the inputs and returns continue to make sense in the context of the overall web app. In any case, the functions either return nothing or they simply return an object whose fields / local variables are identical to each field in the respective table. You can see in a tabular form which functions return an object and which don't.

| Function name | Return details |
|---------------|----------------|
| generateUser() | None |
| obtainUser() | User object (1 record)|
| getProduct() | Product object (1+ records) |
| getProductByID | Product object (1 record) |
| createProduct() | None |
| getKeys() | Key object (1+ records) |
| getKeysBySerialKey() | Key object (1 record) |
| createKey() | ID field of new Key object |
| setKeyState() | None |
| deleteKey() | None |
| resetKey() | None |
| getKeyData() | Key object (1 record) |
| submitLog() | None |
| getKeyLogs() | Changelog object (1+ record) |
| deleteLogs() | None |
| getRegistration() | Registration object (1 record) |
| getKeyHWIDs() | Registration object (1+ records) |
| deleteRegistrationsOfKey() | None |
| addRegistration() | None |