import pyodbc
server = 'REGCONSERVER1'
database = 'itemized'
username = 'belotecainventory'
password = 'belotecainventory'
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = cnxn.cursor()
cnxn1 = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor1 = cnxn1.cursor()

cursor.execute("SELECT * from itemimgdb")
for row in cursor:
    print(row)