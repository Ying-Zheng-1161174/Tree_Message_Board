from TreeOfPeace import connect
import mysql.connector

# Setup Database connection
db_connection = None

def getCursor():
    """
    Get a MySQL cursor with a dictionary format.
    If the connection does not exist or is not connected, it will create a new connection.
    """

    global db_connection
    

    if db_connection is None or not db_connection.is_connected():
        db_connection = mysql.connector.connect(
            user=connect.dbuser,
            password=connect.dbpass,
            host=connect.dbhost,
            auth_plugin='mysql_native_password',
            database=connect.dbname,
            autocommit=True
        )

    cursor = db_connection.cursor(dictionary=True)

    return cursor