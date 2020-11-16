from django.shortcuts import render, HttpResponse
from django.template import Template, RequestContext
import pyodbc
import io
import base64
#SQL server information
server = 'REGCONSERVER1'
database = 'itemized'
username = 'belotecainventory'
password = 'belotecainventory'

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = cnxn.cursor()


# Create your views here.
def main(request):
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()

    cursor.execute("SELECT name from settings where email=?",(request.session['user']))
    name = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(item_name) from solditemdb WHERE 1 >= DATEDIFF(day, date_sold, GETDATE())")
    recentsales = cursor.fetchone()[0]
    return render(request, "newsales.html", {'name': name, 'recentsales': recentsales})

def salesTable(request):
    if request.method == 'GET':
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = cnxn.cursor()
        #Creatingt the sort method
        sort = request.GET["sort"]
        type = request.GET['type']
        fees = request.GET['fees']

        if sort == "sortdate":
            cursor.execute("SELECT solditemdb.item_name, solditemdb.item_retail_price, solditemdb.item_resale_price, solditemdb.item_url, solditemdb.date_sold, solditemdb.sale_status from dbo.solditemdb WHERE solditemdb.email=? ORDER BY solditemdb.date_added", (request.session['user']))
        
        if sort == "sortalpha":
            cursor.execute("SELECT solditemdb.item_name, solditemdb.item_retail_price, solditemdb.item_resale_price, solditemdb.item_url, solditemdb.date_sold, solditemdb.sale_status from dbo.solditemdb WHERE solditemdb.email=? ORDER BY solditemdb.item_name", (request.session['user']))
         
        if sort == "sortlow":
            cursor.execute("SELECT solditemdb.item_name, solditemdb.item_retail_price, solditemdb.item_resale_price, solditemdb.item_url, solditemdb.date_sold, solditemdb.sale_status from dbo.solditemdb WHERE solditemdb.email=? ORDER BY solditemdb.item_resale_price ASC", (request.session['user']))
        
        if sort == "sorthigh":
            cursor.execute("SELECT solditemdb.item_name, solditemdb.item_retail_price, solditemdb.item_resale_price, solditemdb.item_url, solditemdb.date_sold, solditemdb.sale_status from dbo.solditemdb WHERE solditemdb.email=? ORDER BY solditemdb.item_resale_price DESC", (request.session['user']))
        
        if sort != None:
            rows = cursor.fetchall()
            print(rows)
        
        tableString = """
<table id="inventory-table">
    <thead>
        <tr>
            <th>Product</th>
            <th>Retail Price</th>
            <th>Resale Price</th>
            <th>Link</th>
            <th>Date Added</th>
            <th>Status</th>
        </tr>
    </thead>
<tbody>"""
        for row in rows:
            if row[5] == None:
                itemstat = "Just Sold"
            else:
                itemstat = row[5]
            if row[1] == None:
                retail = 0
            else:
                retail = row[1]
            if row[2] == None:
                resale = 0
            else:
                resale = row[2]
            if row[3] == None:
                url = "#"
            else:
                url = row[3]
            tableString = tableString + f"""
<tr>
    <th>{row[0]}</th>
    <th>${retail}</th>
    <th>${resale}</th>
    <th><a href="{url}">Item Link</a></th>
    <th>{row[4]}</th>
    <th class="listed">{itemstat}</th>
</tr>
"""
        tableString = tableString + """
        </tbody>
    </table>
</div>"""
            


    #THIS RENDERS A STRING FROM TEXT
    t = Template(tableString)
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))


def calculateProfit(request):
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()

    cursor.execute("SELECT SUM(item_retail_price), SUM(item_resale_price) from solditemdb WHERE email = ?", request.session["user"])
    row = cursor.fetchone()

    htmlString = """<div class="retailBox">
<h2>
Total Spent
</h2>
<h3>
$%s
</h3>
</div>
<div class="resaleBox">
<h2>
Total Received
</h2>
<h3>
$%s
</h3>
</div>
<div class="profitMarginBox">
<h2>
Total Profits
</h2>
<h3>
$%s
</h3>
</div>
""" % (str(int(row[0])), str(int(row[1])), str(int(row[1]) - int(row[0])))
    print(htmlString)
    template = Template(htmlString)
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def removeItem(request):
    if request.method == "POST":
        itemId = request.DELETE['item']
        cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = cnxn.cursor()
        return HttpResponse("success")
        #cursor.execute("DELETE FROM solditemdb WHERE item_id=? and email=?", (itemId, request.session["user"]))