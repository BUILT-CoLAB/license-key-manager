<p align="center">
  <img src="src/static/logoComplete.svg"/>
</p>

# Multi-Purpose Software License Manager

The Multi-Purpose Software License Manager (SLM, for short) is a web application that is meant to facilitate the management of software distribution.

## Table of Contents

1. Introduction
2. Getting Started
3. Documentation\
   3.1 Directory Structure\
   3.2 Database\
   3.3 RESTful API
4. Helping out

## Intruduction

SLM was initially developed as part of the Captsone Project for the Bachelors of Informatic Engineering of the University of Porto. Taking place as a piece of work for BUILT-CoLAB, the project became open-source and is open for improvements and commercial use as per the terms of the MIT License agreement.

SLM is a Web Application whose main purpose is to help license distributors to manage their existing products, customers and licenses alike. Nowadays, the extreme complexity of the market and the need to reduce the frequency of piracy requires a concise tool that is clear, objective and straightforward. This project was created as a solution to these issues by using a more user-friendly interface that allows for the management of important data features and to observe statistics that are important from a marketing point of view.

The implementation of the web application uses the Flask microframework, in Python 3.9. As a distributor you do not need to do anything other than following the first section of this introductory file. However, as a developer, you are free to check out this entire file in order to learn how to customize / improve the features that SLM offers.

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
docker run -v $(pwd)/src/database:/license-manager/src/database -p 8000:8000 license-manager
```

Windows (Powershell):

```powershell
docker run -v ${PWD}/src/database:/license-manager/src/database -p 8000:8000 license-manager
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

### Directory Structure

As mentioned in previously, the Project uses FLASK, a micro web framework that is written in Python. All the necessary contents are stored in the `src` folder.

In a more graphical way, the directory structure is represented bellow, with some comments to help you out.

```
.
└── src
    └── handlers                                                  # The respective handler for each service route in the RESTful API (called by main.py).
        ├── admins.py
        ├── changelogs.py
        ├── customers.py
        ├── licenses.py
        ├── logs.py
        ├── products.py
        ├── utils.py
        └── validation.py
    └── static                                                    # The containing folder for images, style sheets and javascript.
        ├── dark.mode.handler.js
        ├── dashboardImage.jpg
        ├── default.jpg
        ├── flowbite.min.css
        ├── loginImage.svg
        ├── logoComplete.svg
        ├── style.css
        ├── tailwind.js
        ├── typography.min.css
        └── wallpaperchangelog.jpg
    └── templates                                                 # All pages (.html files) are placed in this folder (called by FLASK when it renders a page).
        ├── 404.html
        ├── base.html
        ├── changelog.html
        ├── cpanel.html
        ├── customers.html
        ├── index.html
        ├── license.html
        ├── product.html
        ├── products.html
        ├── tutorial.html
        └── users.html
    ├── __init__.py                                               # FLASK settings
    ├── auth.py                                                   # API Authentication Endpoints are defined here.
    ├── databaseAPI.py                                            # "Proxy" for database communication.
    ├── keys.py                                                   # License methods are defined here.
    ├── main.py                                                   # General API Endpoints are defined here.
    ├── models.py                                                 # ORM definition of the Database (SQLAlchemy).
    └── sqlite.db                                                 # The SQLite database file.

└── client
    └── clientTest.py                                             # A mock-up of a software trying to communicate with the web application.

└── docs
    └── .............                                             # Used for pedagogical terms and evaluation

└── tests
    └── api                                                       # API Tests
        └── __init__.py
        └── test_admin_functionality.py
        └── test_customer_functionality.py
        └── test_license_functionality.py
        └── test_product_functionality.py
        └── test_security.py
        └── test_validation_functionality.py
    └── unit                                                      # Unit Tests
        └── test_functions.py
        └── test_models.py
    └── __init__.py
    └── conftest.py                                               # Pytest main configuration file


├── .env                                                          # Environment Variables used by Docker
├── Dockerfile                                                    # The Dockerfile used to set-up the Docker Image.
├── README.md                                                     # This documentation.
├── LICENSE.md                                                    # MIT License statement
├── requirements.txt                                              # Used by the pip3 command to install all dependencies
└── server.py                                                     # Python script that runs the web application
```

### Database

The database used in SLM is the SQLite database. The file is present right in the first level of the `src` directory. It is automatically generated by the application if the file does not yet exist. Note, however, that this only occurs once every time you run the application. Deleting the file while the web app is running will effectively render the entire application useless until you restart it.

Also, be aware that when you delete this file, ALL data will be lost. This includes (but is not limited to): User accounts, Products, Licenses, Registered Devices, Customers and even the Changelog. Doing so, will reset the entire project as if you were opening it for the first time. We suggest you to create a routine that generates a backup every now and then in order to prevent the loss of critical data.

When it comes to the documentation of the database, you can check its structure in the `models.py` file. However, in order to help you get through the SQLAlchemy's syntax, we will represent the same information in the file in a tabular format:

| USER Table | Type | PK  | UQ  | AI  | ONDELETE |
| ---------- | ---- | --- | --- | --- | -------- |
| id         | INT  | X   |     | X   | NONE     |
| email      | TEXT |     | X   |     | NONE     |
| password   | TEXT |     |     |     | NONE     |
| name       | TEXT |     | X   |     | NONE     |
| owner      | BOOL |     |     |     | NONE     |
| disabled   | BOOL |     |     |     | NONE     |
| timestamp  | INT  |     |     |     | NONE     |

| PRODUCT Table | Type | PK  | UQ  | AI  | ONDELETE |
| ------------- | ---- | --- | --- | --- | -------- |
| id            | INT  | X   |     | X   | NONE     |
| name          | TEXT |     | X   |     | NONE     |
| category      | TEXT |     |     |     | NONE     |
| image         | TEXT |     |     |     | NONE     |
| details       | TEXT |     |     |     | NONE     |
| privateK      | TEXT |     | X   |     | NONE     |
| publicK       | TEXT |     | X   |     | NONE     |
| apiK          | TEXT |     | X   |     | NONE     |
| lastchecked   | INT  |     |     |     | NONE     |

| CLIENT Table | Type | PK  | UQ  | AI  | ONDELETE |
| ------------ | ---- | --- | --- | --- | -------- |
| id           | INT  | X   |     | X   | NONE     |
| name         | TEXT |     |     |     | NONE     |
| email        | TEXT |     |     |     | NONE     |
| phone        | TEXT |     |     |     | NONE     |
| country      | TEXT |     |     |     | NONE     |
| registrydate | INT  |     |     |     | NONE     |

| KEY Table  | Type | PK  | UQ  | AI  | ONDELETE |
| ---------- | ---- | --- | --- | --- | -------- |
| id         | INT  | X   |     | X   | NONE     |
| productid  | INT  | FK  |     |     | CASCADE  |
| clientid   | INT  | FK  |     |     | CASCADE  |
| serialkey  | TEXT |     | X   |     | NONE     |
| maxdevices | INT  |     |     |     | NONE     |
| devices    | INT  |     |     |     | NONE     |
| status     | INT  |     |     |     | NONE     |
| expirydate | INT  |     |     |     | NONE     |

| REGISTRATION Table | Type | PK  | UQ  | AI  | ONDELETE |
| ------------------ | ---- | --- | --- | --- | -------- |
| id                 | INT  | X   |     | X   | NONE     |
| keyid              | INT  | FK  |     |     | CASCADE  |
| hardwareid         | TEXT |     |     |     | NONE     |

| CHANGELOG Table | Type | PK  | UQ  | AI  | ONDELETE |
| --------------- | ---- | --- | --- | --- | -------- |
| id              | INT  | X   |     | X   | NONE     |
| keyid           | INT  | FK  |     |     | CASCADE  |
| userid          | INT  | FK  |     |     | SET NULL |
| timestamp       | INT  |     |     |     | NONE     |
| action          | TEXT |     |     |     | NONE     |
| description     | TEXT |     |     |     | NONE     |

| VALIDATIONLOG Table | Type | PK  | UQ  | AI  | ONDELETE |
| ------------------- | ---- | --- | --- | --- | -------- |
| id                  | INT  | X   |     | X   | NONE     |
| timestamp           | INT  |     |     |     | NONE     |
| result              | TEXT |     |     |     | NONE     |
| type                | TEXT |     |     |     | NONE     |
| ipaddress           | TEXT |     |     |     | NONE     |
| apiKey              | TEXT |     |     |     | NONE     |
| serialKey           | TEXT |     |     |     | NONE     |
| hardwareID          | TEXT |     |     |     | NONE     |

All modifications in SQLAlchemy are based on this model. You are free to use another database, but you will need to change the Flask settings (`__init__.py` file).

In order to facilitate the transition between databases, the entire web app connects with the database by using the functions in the `databaseAPI.py` file. This means you are free to rewrite these functions, so long the inputs and returns continue to make sense in the context of the overall web app. In any case, the functions either return nothing or they simply return an object whose fields / local variables are identical to each field in the respective table. Some other functions may return specific values. You can see in the table bellow which functions return an object and which don't.

| Function name                | Return details                  |
| ---------------------------- | ------------------------------- |
| generateUser()               | None                            |
| obtainUser()                 | User object (1 record)          |
| createUser()                 | None                            |
| changeUserPassword()         | None                            |
| toggleUserStatus()           | None                            |
| getProduct()                 | Product object (multiple)       |
| getProductCount()            | Integer                         |
| getDistinctClients()         | Integer                         |
| getProductByID               | Product object (1 record)       |
| createProduct()              | Product object (1 record)       |
| editProduct()                | None                            |
| getProductThroughAPI()       | Product object (1 record)       |
| resetProductCheck()          | None (DEBUG ONLY)               |
| getKeys()                    | Key object (multiple)           |
| getKeysBySerialKey()         | Key object (1 record)           |
| createKey()                  | ID field of new Key object      |
| setKeyState()                | None                            |
| deleteKey()                  | None                            |
| resetKey()                   | None                            |
| getKeyData()                 | Key object (1 record)           |
| getKeyStatistics()           | 2 Integers                      |
| getKeyAndClient()            | Key JOIN Customer object        |
| updateKeyStatesFromProduct() | None                            |
| applyExpirationState()       | Key object                      |
| submitLog()                  | None                            |
| getKeyLogs()                 | Changelog object (multiple)     |
| getUserLogs()                | Changelog object (multiple)     |
| queryLogs()                  | Changelog object (multiple)     |
| getRegistration()            | Registration object (1 record)  |
| getKeyHWIDs()                | Registration object (multiple)  |
| deleteRegistrationsOfKey()   | None                            |
| deleteRegistrationOfHWID()   | None                            |
| addRegistration()            | None                            |
| createCustomer()             | None                            |
| modifyCustomer()             | None                            |
| deleteCustomer()             | None                            |
| getCustomer()                | Customer object (multiple)      |
| getCustomerByID()            | Customer object (1 record)      |
| submitValidationLog()        | None                            |
| queryValidationLogs()        | Validationlog object (multiple) |
| queryValidationsStats()      | 2 Integers                      |

## RESTful API Documentation

Listed bellow, you will see the details of our RESTful API. Each endpoint is listed bellow with their respective details.

---

### Login Page

Displays the login-form to enter the Dashboard.<br/><br/>
**Path** : `/`\
**Method** : `GET`\
**Authentication required** : NO\
**Parameters** : NONE\
**Response** : `TEMPLATE_HTML`

---

### Tutorial Page

Displays a tutorial page within the Dashboard.<br/><br/>
**Path** : `/tutorial`\
**Method** : `GET`\
**Authentication required** : YES\
**Parameters** : NONE\
**Response** : `TEMPLATE_HTML`

---

### Dashboard Page

Displays the dashboard page along with the current statistics of the application.<br/><br/>
**Path** : `/dashboard`\
**Method** : `GET`\
**Authentication required** : YES\
**Parameters** : NONE\
**Response** : `TEMPLATE_HTML`

---

### Product List

Displays a webpage with the information of all products in the database, along with their respective details. The administrator is also allowed to create new products or edit existing ones in this webpage.<br/><br/>
**Path** : `/products`\
**Method** : `GET`\
**Authentication required** : YES\
**Parameters** : NONE\
**Response** : `TEMPLATE_HTML`

---

### Product Display

Displays a webpage with the information of an individual product specified in the Path URL of this endpoint. In it, the administrator can check the API Key of the Product, the Public Key and create Licenses.<br/><br/>
**Path** : `/products/id/<productid>`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
PATH:
    productid - The ID of the product we wish to check. Must be a valid ID.
```

**Response** : `TEMPLATE_HTML` or `404` if the productid is invalid.

---

### Create Product

Creates a product with the details specified in its body payload. The input must be in JSON format as a dictionary.<br/><br/>
**Path** : `/products/create`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
BODY:
    {
        'name' : 'Product name',
        'category' : 'Product category',
        'image' : 'Product image',
        'details' : 'Product details'
    }
```

**Response** : A `RESPONSE_FORM`\*.

---

### Edit Product

Modifies the data of an existing product with the details specified in its body payload. The input must be in JSON format as a dictionary.<br/><br/>
**Path** : `/products/edit`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
BODY:
    {
        'id' : 'The ID of the product which data we want to edit'
        'name' : 'Product name',
        'category' : 'Product category',
        'image' : 'Product image',
        'details' : 'Product details'
    }
```

**Response** : A `RESPONSE_FORM`\*.

---

### Customer List

Displays a webpage with the all the necessary information about existing Customers. The administrator can also create new Customers, modify their data or even remove existing ones.
**Path** : `/customers`\
**Method** : `GET`\
**Authentication required** : YES\
**Parameters** : NONE\
**Response** : `TEMPLATE_HTML`

---

### Create Customer

Adds a Customer to the database with the details specified in its body payload. The input must be in JSON format as a dictionary.<br/><br/>
**Path** : `/customers/create`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
BODY:
    {
        'name' : 'Customer's name',
        'email' : 'Customer's email',
        'phone' : 'Customer's phone number',
        'country' : 'Customer's country'
    }
```

**Response** : A `RESPONSE_FORM`\*.

---

### Edit Customer

Modifies the data of an existing customer with the new details specified in its body payload. The input must be in JSON format as a dictionary.<br/><br/>
**Path** : `/customers/edit/<customerid>`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
PATH:
    customerid (?URL) - The ID of the Customer whose data we wish to modify. Must be a valid ID.
BODY:
    {
        'name' : 'Customer's name',
        'email' : 'Customer's email',
        'phone' : 'Customer's phone number',
        'country' : 'Customer's country'
    }
```

**Response** : A `RESPONSE_FORM`\*.

---

### Delete Customer

Deletes the data of an existing customer specified in the URL Path of the endpoint.<br/><br/>
**Path** : `/customers/delete/<customerid>`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
PATH:
    customerid - The ID of the Customer we wish to remove.
```

**Response** : A `RESPONSE_FORM`\*.

---

### Create License

Creates a license assigned to the Product specified in the URL Path of the endpoint.<br/><br/>
**Path** : `/product/<productid>/createlicense`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
PATH:
    productid - The ID of the Product we wish to assign this License to. It must be valid.
BODY:
    {
        'client' : 'The ID of the customer we will assign this License to',
        'maxDevices' : 'The limit of concurrent devices in this License',
        'expiryDate' : 'Expiration date for this License'
    }
```

**Response** : A `RESPONSE_FORM`\*.

---

### Display License

Displays a webpage with the all the necessary information about existing Customers. The administrator can also create new Customers, modify their data or even remove existing ones.<br/><br/>
**Path** : `/licenses/<licenseid>`\
**Method** : `GET`\
**Authentication required** : YES\
**Parameters** :

```
PATH:
    licenseid (?URL) - The ID of the License we wish to assign this License to. It must be valid.
```

**Response** : `TEMPLATE_HTML`

---

### Edit License State

Changes the underlying information of the License by either disabling/enabling it, deleting it or completely reseting it.<br/><br/>
**Path** : `/licenses/editkeys`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
BODY:
    {
        'licenseid' : 'The ID of the customer we will assign this License to',
        'action' : 'The action that will be executed. Can be: SWITCHSTATE, DELETE or RESET'
    }
```

**Response** : A `RESPONSE_FORM`\*.

---

### Unlink device from License

Unlinks a device through its Hardware ID from the License.<br/><br/>
**Path** : `/licenses/<keyid>/removedevice`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
PATH:
    keyid - The ID of the License we will unlink the Hardware from
BODY:
    {
        'hardwareID' : 'The ID of the hardware to be unlinked (unique for every device)'
    }
```

**Response** : A `RESPONSE_FORM`\*.

---

### Display Changelog

Displays a Page where the changelogs will be displayed based on the settings chosen in the form inside.<br/><br/>
**Path** : `/logs/changes`\
**Method** : `GET`\
**Authentication required** : YES\
**Parameters** : NONE
**Response** : A `RESPONSE_FORM`\*.

---

### Get Logs

Acquires the change logs that fit the criteria sent through the Header.<br/><br/>
**Path** : `/logs/changes/query`\
**Method** : `GET`\
**Authentication required** : YES\
**Parameters** :

```
HEADER:
    {
        |OPTIONAL| 'adminID' : 'The ID of the administrator whose logs we want to check',
        |OPTIONAL| 'datestart' : 'The date that defines the start of our search',
        |OPTIONAL| 'dateend' : 'The date that defines the limit of our search',
    }
```

**Response** : A `JSON` dictionary array containing the 'adminid', 'timestamp' and 'description' for each log.

---

### Display Validation Log

Displays a Page where the validation logs will be displayed based on the settings chosen in the form inside.<br/><br/>
**Path** : `/logs/validations`\
**Method** : `GET`\
**Authentication required** : YES\
**Parameters** : NONE
**Response** : A `RESPONSE_FORM`\*.

---

### Get Logs

Acquires the validation logs that fit the criteria sent through the Header.<br/><br/>
**Path** : `/logs/validations/query`\
**Method** : `GET`\
**Authentication required** : YES\
**Parameters** :

```
HEADER:
    {
        |OPTIONAL| 'typeSearch' : 'The type of logs we will be looking for. Successful attempts or failed attempts.',
        |OPTIONAL| 'datestart' : 'The date that defines the start of our search',
        |OPTIONAL| 'dateend' : 'The date that defines the limit of our search',
    }
```

**Response** : A `JSON` dictionary array containing the Validationlog table rows obtained from the query.

---

### Get Admins

Displays a webpage containing all the admins in the page. Only users flagged as 'Owners' can see this page and they can create admin accounts, disable them or redefine their passwords as they see fit.<br/><br/>
**Path** : `/admins`\
**Method** : `GET`\
**Authentication required** : YES (Restricted to Owners)\
**Parameters** : NONE
**Response** : `TEMPLATE_HTML`

---

### Create Admin Account

Creates an admin account that will be allowed to log in and act as an administrator. The data about the account must be sent in JSON format as a dictionary through the payload.<br/><br/>
**Path** : `/admins/create`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
BODY:
    {
        'email' : 'The admin's email',
        'username' : 'The admin's username',
        'password' : 'The admin's password'
    }
```

**Response** : A `RESPONSE_FORM`\*.

---

### Edit Admin Account

Modifies a specified admin account. This endpoint is, in fact, used only to re-define the password of the specified admin.<br/><br/>
**Path** : `/admins/<userid>/edit`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
PATH:
    userid - The admin account's ID that we wish to modify.
BODY:
    {
        'password' : 'The new password that will be assigned to the admin'
    }
```

**Response** : A `RESPONSE_FORM`\*.

---

### Toggle Admin Account State

Enables or Disables the specified Admin Account based on the current status of the account.<br/><br/>
**Path** : `/admins/<userid>/togglestatus`\
**Method** : `POST`\
**Authentication required** : YES\
**Parameters** :

```
PATH:
    userid - The admin account's ID that will have its state changed (disabled or enabled)
```

**Response** : A `RESPONSE_FORM`\*.

---

### Validation

Validates a request coming from any external source to decipher whether or not the validation request is valid and that the license indicated is, in fact, genuine. The response follows the same format for all cases.<br/><br/>
**Path** : `/api/v1/validate`\
**Method** : `POST`\
**Authentication required** : NO\
**Parameters** :

```
BODY:
{
    'apiKey' : 'The API Key of the Product that the customer's license belongs to. Used to locate the product'
    'payload' : 'A PublicKey-encrypted message that containts the HardwareID and the Serial Key of the License'
}
```

**Response** : A `JSON` dictionary array containing four fields. It has a code indicating whether or not the validation succeeded (if the code starts with `ERR_` then the validation failed). It also has a description elaborating the reason why it failed.

\*`RESPONSE_FORM` - For every single endpoint above, this type of JSON dictionary response carries a CODE and a MESSAGE. The CODE is used by the script to know if the request succeeded. If it didn't, then the javascript will show the server-generated message to the client. Example:

```json
{
    'HttpCode' : str(HTTPCode),
    'Message' : str(Message),
    'Code' : str(ResponseCode),
    'SerialKey' : str(key),
    'HardwareID' : str(hwid),
    'ExpirationDate' : int( -1 ) || int( expirationDate )
}
```

## Contributing Guidelines

SLM is still a work in progress and is completely available for improvement. You can help out by:

- Suggesting changes to the code by submitting issues
- Making your own changes and requesting merge pulls
- Creating your own version based on the current state of this project
- Patching critical security issues

You are also encouraged to write unit tests for new functionalities or even existing ones. Although one of the achievements of this application is to make a clear and readable interface, ensuring security is still the top priority in the issue list. Make sure to tag any security issues clearly.

### Style

- Linter: `pylint`
- Formatter: `autopep8`
