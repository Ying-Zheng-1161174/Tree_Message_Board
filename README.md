# Tree of Peace

Trees and hedges can lead to disputes between neighbors, such as falling leaves or blocked views. This app helps homeowners find peaceful solutions to these issues without resorting to drastic measures like chainsaws. Join the platform to communicate with others and resolve tree-related conflicts in a friendly and effective way.

## Running This App

1. Open the project in Visual Studio Code.

2. Create a virtual environment and activate it:

```
python -m venv venv
```

On Windows:

```
venv\Scripts\activate
```

On macOS:

```
source venv/bin/activate
```

3. Install the dependencies by running:

```
pip install -r requirements.txt
```

4. Open 'treeofpeace_pa.sql' in MySQL, and add the following code at the top of the file to create your local database:

```
DROP SCHEMA IF EXISTS treeofpeace;
CREATE SCHEMA treeofpeace;
USE treeofpeace;
```

5. Create a file in the TreeOfPeace folder named connect.py (TreeOfPeace/connect.py) with the following connection details:

```
# These details are available on the first MySQL Workbench screen
# Usually called 'Local Instance'

dbuser = "root"  # Put your MySQL username here - usually root
dbpass = "xxxxxx"  # Put your password here
dbhost = "localhost"
dbport = "3306"
dbname = "treeofpeace"
```

6. Run the app in your terminal:

```
python run.py
```

You should be able to view the app at: http://127.0.0.1:5000

Enjoy!

## About the App

1. Users who register will be assigned a default role of 'member'.
2. The only way to create 'moderator' and 'admin' roles is to insert them directly into the database.
3. Admins and Moderators can delete anyone's messages and replies.
4. Admins can modify a user's role and status.
5. You can register a new account or use the existing accounts to try it out. Usernames and passwords are as follows:

```
'member1', 'member1pass',
'member2', 'member2pass', and so on.
'moderator1', 'moderator1pass',
'moderator2', 'moderator2pass',
'admin1', 'admin1pass',
'admin2', 'admin2pass',
```
