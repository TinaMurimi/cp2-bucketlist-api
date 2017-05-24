# cp2-bucketlist-api

# What does this PR do?
Modelling a room allocation system for one of Andela’s facilities called Amity

# Description of Task to be completed
1. Print message if no people or rooms exist when list functions are called
2. Restrict adding people with similar names
3. Allow allocation of people who had no previous allocations
4. Allow for allocation to a specified person
5. Print message if no allocations exist when the print_allocations function is called
6. Implement tearDown in tests
7. Docstring consistency
8. Remove unused code
9. SETTINGS.py for root directory

# Building blocks
1. Python 3
2. SQLite3

# How should this be manually tested?

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

**To run the application**

        $ python main.py

**To run the test**
* Create a .coveragerc file

        $ touch .coveragerc

* Add the files you do not want covered. Eg.:
     ```
     [run]
     omit =
         psycopg2.py
         */psycopg2/*
         sqlalchemy.py
         */sqlalchemy/*
         *decimal.py
         *numbers.py
         sqlite3.py
         */sqlite3/*
         *tabulate.py
     ```

* Run the test:

        $ nosetests

* To check the coverage

        $ nosetests --with-coverage

# Project Demo
[https://asciinema.org/a/119230](url)
# Screenshots
This is a cli application. Run the main.py

<img width="863" alt="amity screenshot" src="https://cloud.githubusercontent.com/assets/26300276/25145960/19a00d42-247b-11e7-95e1-fda23e5be435.png">
