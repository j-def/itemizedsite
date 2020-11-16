import pyodbc

server = 'REGCONSERVER1'
database = 'itemized'
username = 'belotecainventory'
password = 'belotecainventory'


cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = cnxn.cursor()

cursor.execute("SELECT img_1 from imgdb")
for row in cursor:
    print(row)