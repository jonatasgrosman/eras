# INITIAL SETUP

## Install dependecies

- install MongoDB (www.mongodb.com)
- install FreeLing (https://github.com/TALP-UPC/FreeLing)
- install Python 3.x
- install Python package dependencies using `requirements.txt` file
- install Gunicorn (https://gunicorn.org/)

## Config variables

- go to the `__init__.py` file of each module e change its variables if needed. Note that if you redefine the SECRET_KEY of authentication module, you'll need to recreate the default passwords using the `authentication/module/util/cryptUtil.py` script

## Config DB

- go to the mongoDB console

`mongo`

- creating authentication DB

`use authentication`

- creating unique key

`db.users.createIndex( { "email": 1 }, { unique: true } )`

- adding default users

`db.users.insert({"firstName":"admin", "lastName":"", "email":"admin@eras", "password":"o51WhrOqtptLoIqILOOlVSSZ9jAnyTLeaFfn8Eg/XRWGeiJN4RBVD9OpFpJ71bCo", "role":"ADMIN"})`

`db.users.insert({"firstName":"", "lastName":"", "email":"nlp@eras", "password":"o51WhrOqtptLoIqILOOlVSSZ9jAnyTLeaFfn8Eg/XRWGeiJN4RBVD9OpFpJ71bCo", "role":"MODULE"})`

`db.users.insert({"firstName":"", "lastName":"", "email":"data@eras", "password":"o51WhrOqtptLoIqILOOlVSSZ9jAnyTLeaFfn8Eg/XRWGeiJN4RBVD9OpFpJ71bCo", "role":"MODULE"})`

# EXECUTION

- run Freeling instances (change the port parameter if necessary)

`analyze -f pt.cfg --nonumb --noloc --noner --nodict --outlv tagged --server --flush --port 50040`

`analyze -f en.cfg --nonumb --noloc --noner --nodict --outlv tagged --server --flush --port 50050`

`analyze -f pt.cfg --outlv tagged --server --flush --port 50041`

`analyze -f en.cfg --outlv tagged --server --flush --port 50051`

- run ERAS API

`gunicorn --chdir authentication -b 0.0.0.0:50000 --log-level debug run:app`

`gunicorn --chdir data -b 0.0.0.0:50001 --log-level debug run:app`

`gunicorn --chdir nlp -b 0.0.0.0:50002 --log-level debug run:app`

- run ERAS client

go to /client folder and run `python3 -m http.server 80`

- To check if everything is working properly, go to http://localhost, sign in using admin credentials and use the files contained in /samples folder to create a project and make some annotations