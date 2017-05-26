# CP2A - BucketList Application API

# Problem Description
The BucketList Application API is an online Bucket List service using Flask.

According to Merriam-Webster Dictionary, a Bucket List is a list of things that one has not done before but wants to do before dying.

| URL Endpoint | HTTP Methods | Summary |
| -------- | ------------- | --------- |
| `/bucketlist_api/v1.0/auth/register` | `POST`  | Register a new user|
| `/bucketlist_api/v1.0/users` | `GET`  | List all registered users|
| `/bucketlist_api/v1.0/auth/login` | `POST` | Login and generate aunthentication token|
| `/bucketlist_api/v1.0/user/<int:id>` | `GET` | Get user profile/details|
| `/bucketlist_api/v1.0/user/<int:id>` | `PUT` | Edit user profile/details|
| `/bucketlist_api/v1.0/user/<int:id>` | `DELETE` | Delete a user|
| `/bucketlist_api/v1.0/bucketlists` | `POST` | Create a new Bucketlist|
| `/bucketlist_api/v1.0/bucketlists` | `GET` | Retrieve all bucketlists for user|
| `/bucketlist_api/v1.0/bucketlists?limit=<int:number>` | `GET` | Limit the results to retrieve per page|
| `/bucketlist_api/v1.0/bucketlists?q=<name>` | `GET` | Search for a bucketlist with the word/name|
| `/bucketlist_api/v1.0/bucketlists/<int:id>` | `GET` |  Retrieve bucket list details |
| `/bucketlist_api/v1.0/bucketlists/<int:id>` | `PUT` | Update bucket list details |
| `/bucketlist_api/v1.0/bucketlists/<int:id>` | `DELETE` | Delete a bucket list |
| `/bucketlist_api/v1.0/bucketlists/<int:id>/items` | `POST` |  Create items in a bucket list |
| `/bucketlist_api/v1.0/bucketlists/<int:id>/items/<int:item_id>` | `PUT`| update a bucket list item details|
| `/bucketlist_api/v1.0/bucketlists/<int:id>/items/<int:item_id>` | `DELETE`| Delete a item in a bucket list|

# Building blocks
1. Python 3
2. Postgresql

# Setting up

**Prepare virtual environment**
* To install virtualenvwrapper, we will first install virtualenv

        $ pip install virtualenv
        $ pip install virtualenvwrapper

* Next, create a folder that will contain all your virtual environments:

        $ mkdir ~/.virtualenvs

* Open your .bashrc file and add:

        $ export WORKON_HOME=~/.virtualenvs
        $ source /usr/local/bin/virtualenvwrapper.sh

* You can activate these changes by typing

        $ source .bashrc

* Quit the current terminal and reopen it to execute the script and start working with virtualenvwrapper.

* To create a virtual environment

        $ mkvirtualenv --python=python3_path <environment_name>

* python3_path is the path of python3, which can be found with

        $ which python3

* To activate a virtual environment

        $ workon <environment_name>

* To deactivate it, just type:

        $ deactivate

* To delete a virtual environment

        $ rmvirtualenv <environment_name>

**Check out the project**

        $ git clone https://github.com/tinamorale/cp1-amity-allocation/

**Install requirements into virtualenvwrapper:**

        $ pip install -r requirements.txt

**Create a .env file:**

* Create the .env file in the root folder

        $ touch .env

* Add the following to the file

        workon <environment_name>
        export FLASK_APP="manage.py"
        export SECRET_KEY="Your secret key"
        export APP_SETTINGS="development"
        export SQLALCHEMY_DATABASE_URI="postgresql://postgres@localhost/bucketlist"

* Export the settings

        $ source .env

* To view settings details use

        $ echo $SECRET_KEY

**To run the application**

* Create the db

        $ python manage.py db init
        $ python manage.py db migrate
        $ python manage.py db upgrade

* Create an Admin user

        $ python manage.py createuser

* Install postman, a Google Chrome extension, then run:

        $ python manage.py runserver

* .....or alternatively

        $ flask run
        
<img width="681" alt="screen shot 2017-05-25 at 11 31 54" src="https://cloud.githubusercontent.com/assets/26300276/26443077/aa8e2704-413f-11e7-8131-039682641868.png">


* In bucketlist/app/__init__.py, see all the URIs for different feature. Copy the URI in Postman, eg:

[http://127.0.0.1:5000/bucketlist_api/v1.0/auth/login](url)
        
       

<img width="1116" alt="screen shot 2017-05-25 at 11 52 19" src="https://cloud.githubusercontent.com/assets/26300276/26443146/ebb64464-413f-11e7-839d-f36a9022fe54.png">


<img width="1410" alt="screen shot 2017-05-25 at 12 51 27" src="https://cloud.githubusercontent.com/assets/26300276/26445255/2da90a20-4148-11e7-89b8-64090817b481.png">

**Deploying to Heroku**

* Create a Heroku account online

* Install the Heroku CLI. If using Mac OS X, run

        $ brew install heroku


* Log in using the email address and password you used when creating your Heroku account

        $ heroku login

* Create an app on Heroku, which prepares Heroku to receive your source code

        $ heroku apps:create <app_name>

* Create a Procfile in the root folder

        $ touch Procfile

* ..... and add the following


        web: gunicorn --workers 4 --bind "0.0.0.0:$PORT" flask_app:app --log-file -


* Create a runtime.txt file

        $ touch runtime.txt

* ..... and add the following

        python-3.6.0 

* Now deploy your code:

        $ git push heroku master

* If using a branch other than master:

        $ git push heroku <branch_name>:master

* The application is now deployed. Ensure that at least one instance of the app is runnin

        $ heroku ps:scale web=1

* Now visit the app at the URL generated by its app name. As a handy shortcut, you can open the website as follows:
        
        $ heroku open
        
* See it in action

[https://cp2a-bucketlist-api.herokuapp.com/](url)

**To run the test**
* Create a .coveragerc file

        $ touch .coveragerc

* Add the files you do not want covered. Eg.:
     ```
     [run]
     omit =
         psycopg2.py
         */psycopg2/*
         */flask_sqlalchemy/*
     ```

* Run the test:

        $ nosetests

* To check the coverage

        $ nosetests --with-coverage
