import mysql.connector

def connection():
    con = mysql.connector.connect(host = "localhost", user = "root", password = "", database = "oees", buffered=True)
    cur = con.cursor()
    
    return cur, con

try:
    cur, con = connection()
    
    with open('oees.sql', 'r') as file:
        commands = file.read()
        
    sql_commands = commands.split(';')

    for command in sql_commands:
        cur.execute(command)
        con.commit()

    print("SQL commands executed successfully.")
except Exception as e:
    print("Error executing SQL commands:", e)
finally:
    if con.is_connected():
        cur.close()
        con.close()
        print("MySQL connection closed.")
