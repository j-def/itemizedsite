from django.shortcuts import render, HttpResponse
from django.template import Template, RequestContext
from django.http import StreamingHttpResponse
import pyodbc
import hashlib
import random
import string
import os
import io
import base64
import requests
import re


#SQL server information
server = 'REGCONSERVER1'
database = 'itemized'
username = 'belotecainventory'
password = 'belotecainventory'

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = cnxn.cursor()
# Create your views here.

def home(request):
    try:
        #Checks if the user is already logged in
        request.session["user"]

        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = cnxn.cursor()

        cursor.execute("SELECT settings.name, AVG(DATEDIFF(day, solditemdb.date_added, solditemdb.date_sold))   from dbo.settings, dbo.solditemdb WHERE settings.email=?  group by settings.name", (request.session["user"]))
        respdata = cursor.fetchone()
        name = respdata[0]
        avgwait = respdata[1]


        cursor.execute("SELECT count(itemdb.date_posted) from dbo.itemdb WHERE itemdb.email = ? ", (request.session["user"]))
        respdata = cursor.fetchone()
        totallivelistings = respdata[0]

        cursor.execute("SELECT count(solditemdb.date_sold) from dbo.solditemdb WHERE solditemdb.email = ?", (request.session["user"]))
        respdata = cursor.fetchone()
        totalsoldlistings = respdata[0]

        cursor.execute("SELECT count(solditemdb.date_sold) from dbo.solditemdb WHERE solditemdb.email = ? AND 1 >= DATEDIFF(day, solditemdb.date_sold, GETDATE())", (request.session["user"]))
        respdata = cursor.fetchone()
        dailysales = respdata[0]


        #Gotta grab name
        #Avg time listings to sit on markets,
        #Total live listings,
        #total sold listings
        #, sales in past 24 hours,

        #Javascript to grab, new inventory,
        #total profit, sales, and recent inventory additions


        return render(request, "newhome.html", {"name":name, "dailysales": dailysales, "avglistingtime": avgwait, "totallivelistings": totallivelistings, "totalsoldlistings": totalsoldlistings})
    except:
        return HttpResponse("Error accessing home page.")


##############Listings########################

def listings(request):
    # Checks if the user is logged in and then renders the add product html page
    try:
        request.session["user"]
        return render(request, "listings.html")
    except:
        return render(request, "redirect.html", {"redirect": "/"})


##############settings########################

def settings(request):
    # Checks if the user is logged in and then renders the settings page
    try:
        email = request.session["user"]

        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = cnxn.cursor()

        cursor.execute("SELECT name from dbo.settings WHERE email=?", request.session["user"])
        name = cursor.fetchone()[0]


        return render(request, "settings.html", {'name': name})
    except:
        return render(request, "redirect.html", {"redirect": "/"})

#When the user presses update settings in the settings page, this function runs
def updateSettings(request):
    if request.method == "GET":
        #Storing all the data in a dictionary

        userSettingData = {}

        userSettingData["mercariemail"] = "'" + request.GET["mercariemail"] + "'"
        userSettingData["mercaripass"] = "'" + request.GET["mercaripass"] + "'"

        #Sets up the userSettingData dictionary to the correct format for the sql command
        for setting in userSettingData:
            if userSettingData[setting] == "''":
                userSettingData[setting] = "NULL"

        cursor.execute("UPDATE settings SET mercari_user=%s, mercari_password=%s WHERE email='%s'" % (userSettingData["mercariemail"],
                                                                                      userSettingData["mercaripass"],
                                                                                                      request.session["user"]))
        cnxn.commit()

        return HttpResponse("success")


##############Inventory#######################

#Sends the user to the edit page for an item selected in the inventory page
def edit(request):
    if request.method == "GET":

        #grabbing the id of the product
        productid = request.GET["id"]


        #grabbing all the images for the product id
        cursor.execute("SELECT img_1, img_2, img_3, img_4, img_5,img_6 from imgdb WHERE item_id = '%s'" % productid)

        for row in cursor:
            imgContainer = []
            for img in row:
                if img != None:
                    imgContainer.append(img)

        cursor.execute("SELECT item_name, item_retail_price, item_resale_price, item_url, item_title, item_description, shipping_cost from dbo.itemdb WHERE item_id = '%s'" % productid)
        for row in cursor:
            itemDict = {}
            itemDict["name"] = row[0]
            itemDict["item_retail"] = row[1]
            itemDict["item_resale"] = row[2]
            itemDict["url"] = row[3]
            itemDict["title"] = row[4]
            itemDict["description"] = row[5]
            itemDict["shipping_cost"] = row[6]

        #correcting the format for the html doc
        for item in itemDict:
            if itemDict[item] == None:
                itemDict[item] = ""

        notfree = ""
        free = ""
        if itemDict["shipping_cost"] == "free":
            free = "selected"
        if itemDict["shipping_cost"] == "notFree":
            notfree = "selected"

        #special formatting for the costs
        if itemDict["item_resale"] == None or itemDict["item_resale"] == "":
            itemDict["item_resale"] = int(float(0))
        if itemDict["item_retail"] == None or itemDict["item_retail"] == "":
            itemDict["item_retail"] = int(float(0))

        itemDict["item_resale"] = int(float(itemDict["item_resale"]))
        itemDict["item_retail"] = int(float(itemDict["item_retail"]))


        print(itemDict)
        return render(request, "editproduct.html", {"name": itemDict["name"], "url": itemDict["url"],
                                                    "title": itemDict["title"], "description": itemDict["description"],
                                                    "resale": itemDict["item_resale"], "retail": itemDict["item_retail"],
                                                    "notfree": notfree, "free": free, "id": productid})

#Sends a html document to render images for an item id
def editItemImages(request):
    # initiating the SQL connection
    if request.method == "GET":
        productid = request.GET["id"]

        # grabbing all the images for the product id
        cursor.execute("SELECT img_1, img_2, img_3, img_4, img_5, img_6 from imgdb WHERE item_id = '%s'" % productid)


        #creating a list of all the images
        for row in cursor:
            imgContainer = []
            for img in row:
                if img != None:
                    imgContainer.append(img)

        imgHtml = ""
        #Creating the html document for the images
        for image in imgContainer:
            stream_str = io.BytesIO(image)
            image = base64.b64encode(stream_str.getvalue())
            imgHtml = imgHtml + "\n<img src=\"data:;base64,{}\" alt=\"Image Failed to Load\" id=\"images\">".format(str(image)[2:-1])


        #Saving the html document
        with open("templates/editproductimg.html", "w") as file:
            file.write(imgHtml)

        #sending the html to render the images
        return render(request, "editproductimg.html")

def saveEdits(request):
    if request.method == "POST":
        # Storing all the post data in a dictionary

        product = {}
        product["name"] = request.POST["name"]
        product["url"] = request.POST["url"]
        try:
            product["title"] = request.POST["customTitle"]
        except:
            product["title"] = ""
        try:
            product["desc"] = request.POST["customDesc"]
        except:
            product["desc"] = ""
        product["shippingcost"] = request.POST["shippingCost"]

        # Money is special case (Listing Price and Purchase Price)
        try:
            product["listingprice"] = request.POST["listingPrice"]
            if product["listingprice"] == "":
                product["listingprice"] = 0
        except:
            product["listingprice"] = "NULL"
        try:
            product["purchaseprice"] = request.POST["purchasePrice"]
            if product["purchaseprice"] == "":
                product["purchaseprice"] = 0
        except:
            product["purchaseprice"] = 0

        # Generating the id for the item the user is inputting
        productid = request.POST["id"]

        # Dictionary to store images
        imageDict = {
            "img1": None,
            "img2": None,
            "img3": None,
            "img4": None,
            "img5": None,
            "img6": None
        }

        # List of images sent from the form
        images = request.FILES.getlist("imageBox")

        #Creating a dictionary for the image names
        ignoreImageUpdate = True

        imgcount = 0

        if len(images) > 0:
            my_dir = "./images/"
            for fname in os.listdir(my_dir):
                if productid in fname:
                    print(fname)
                    os.remove(os.path.join(my_dir, fname))

        for image in images:
            ignoreImageUpdate = False
            imgBytes = image.file.getvalue()
            imgcount += 1
            # making the name of the image file **UNIQUE NAME**
            imageDict["img" + str(imgcount)] = imgBytes

        for info in product:
            if product[info] != "" and info != "listingprice" and info != "purchaseprice":
                product[info] = "'"+ product[info] +"'"
            if product[info] == "":
                product[info] = "Null"


        #Building the sql command to update the data base
        command = "UPDATE itemdb SET item_name = %s, item_retail_price = %s, item_resale_price = %s, item_url = %s," \
                  " item_title = %s, item_description = %s, shipping_cost = %s WHERE item_id = '%s' AND email = '%s'" % (product["name"],
                                                                                   product["purchaseprice"],
                                                                                   product["listingprice"],
                                                                                   product["url"], product["title"],
                                                                                   product["desc"], product["shippingcost"], productid, request.session["user"])

        cursor.execute(command)
        cnxn.commit()


        if ignoreImageUpdate == False:
            cursor.execute("UPDATE imgdb SET img_1 = ?, img_2 = ?, img_3 = ?, img_4 = ?, img_5 = ?, img_6 = ? "
                            "WHERE item_id = ?", (imageDict["img1"], imageDict["img2"], imageDict["img3"],
                                                  imageDict["img4"], imageDict["img5"], imageDict["img6"], productid))
            cnxn.commit()

        return render(request, "redirect.html", {"redirect":"/inventory"})

#Sends the base html for the inventory table page
def inventory(request):
     cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
     cursor = cnxn.cursor()

     cursor.execute("SELECT name from settings where email=?",(request.session['user']))
     name = cursor.fetchone()[0]

     cursor.execute("SELECT COUNT(item_name) from itemdb WHERE 1 >= DATEDIFF(day, date_posted, GETDATE())")
     newitemscount = cursor.fetchone()[0]

     return render(request, "newinventory.html", {'name':name, 'newitems': newitemscount})

#Builds and sends the inventory table
def buildInventoryTable(request):
    if request.method == 'GET':
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = cnxn.cursor()
        #Creatingt the sort method
        sort = request.GET["sort"]
        type = request.GET['type']
        fees = request.GET['fees']

        if sort == "sortdate":
            cursor.execute("SELECT itemdb.item_name, itemdb.item_retail_price, itemdb.item_resale_price, itemdb.item_url, itemdb.date_added, itemdb.date_posted from dbo.itemdb WHERE itemdb.email=? ORDER BY itemdb.date_added", (request.session['user']))
        
        if sort == "sortalpha":
            cursor.execute("SELECT itemdb.item_name, itemdb.item_retail_price, itemdb.item_resale_price, itemdb.item_url, itemdb.date_added, itemdb.date_posted from dbo.itemdb WHERE itemdb.email=? ORDER BY itemdb.item_name", (request.session['user']))
         
        if sort == "sortlow":
            cursor.execute("SELECT itemdb.item_name, itemdb.item_retail_price, itemdb.item_resale_price, itemdb.item_url, itemdb.date_added, itemdb.date_posted from dbo.itemdb WHERE itemdb.email=? ORDER BY itemdb.item_resale_price ASC", (request.session['user']))
        
        if sort == "sorthigh":
            cursor.execute("SELECT itemdb.item_name, itemdb.item_retail_price, itemdb.item_resale_price, itemdb.item_url, itemdb.date_added, itemdb.date_posted from dbo.itemdb WHERE itemdb.email=? ORDER BY itemdb.item_resale_price DESC", (request.session['user']))
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
                itemstat = "Building"
            else:
                itemstat = "Listed"
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


#Adds to the inventory database
def addItem(request):
    #Checks if the user is logged in and then renders the add product html page
    try:
        request.session["user"]
        return render(request, "addproduct.html")
    except:
        return render(request, "redirect.html", {"redirect": "/"})

#Taking post data from addItem and putting it in the sql database
def addItemToDB(request):
    #Making sure the user is logged in
    request.session["user"]
    if request.method == "POST":

        #Storing all the post data
        productName = request.POST["name"]
        productURL = request.POST["url"]
        try:
            customTitle = request.POST["customTitle"]
        except:
            customTitle = ""
        try:
            customDesc = request.POST["customDesc"]
        except:
            customDesc = ""
        shippingCost = request.POST["shippingCost"]

        #Money is special case (Listing Price and Purchase Price)
        try:
            listPrice = request.POST["listingPrice"]
            if listPrice == "":
                listPrice = 0
        except:
            listPrice = "NULL"
        try:
            purchasePrice = request.POST["purchasePrice"]
            if purchasePrice == "":
                purchasePrice = 0
        except:
            purchasePrice = 0

        # Generating the id for the item the user is inputting
        itemid = request.session["user"] + ''.join(random.choice(string.ascii_lowercase) for i in range(25))

       #Dictionary to store images
        imageDict = {
            "img1": None,
            "img2": None,
            "img3": None,
            "img4": None,
            "img5": None,
            "img6": None
        }

        #List of images sent from the form
        images = request.FILES.getlist("images")

        imgcount = 0
        for image in images:
            imgcount += 1
            imgBytes = image.file.getvalue()

            #making the name of the image file **UNIQUE NAME**
            imageDict["img"+str(imgcount)] = imgBytes



        if int(float(listPrice)) == 0:
            listPrice = ""
        if int(float(purchasePrice)) == 0:
            purchasePrice = ""

        variableList = [itemid, productName, purchasePrice, listPrice, productURL, customTitle, customDesc,shippingCost]
        variables = "'"+request.session["user"]+"'"
        for variable in variableList:
            if variable == "":
                variables = variables + ",NULL"
            else:
                variables = variables + ",'%s'" % str(variable)

        #Inserting the item into the database except for image names
        cursor.execute("INSERT INTO dbo.itemdb (email,  item_id ,item_name, item_retail_price, item_resale_price, item_url, item_title, item_description, shipping_cost) VALUES (%s)" % (variables))
        cnxn.commit()

        cursor.execute("INSERT INTO dbo.imgdb (item_id, img_1, img_2, img_3, img_4, img_5, img_6) VALUES (?,?,?,?,?,?,?)",
                       (itemid, imageDict["img1"],imageDict["img2"],imageDict["img3"],imageDict["img4"],imageDict["img5"],imageDict["img6"]))
        cnxn.commit()

        return render(request, "redirect.html", {"redirect": "/inventory"})




##############Signup##########################
#Send the base html to sign up
def signup(request):
    try:
        #Checks if the user is already logged in
        request.session["user"]
        return render(request, "redirect.html", {"redirect": "/"})
    except:
        return render(request, "newsignup.html")

#Function to create the account
def signupCreate(request):
    if request.method == "GET":

        #Getting the information from the user
        email = request.GET["email"]
        password1 = request.GET["password"]

        #Checking is the email input is already in use
        emailInUse = False
        cnxn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = cnxn.cursor()

        #Retreiving any info related to the input email
        cursor.execute("SELECT * from logindb WHERE  email = '%s'" % email)
        for row in cursor:
            emailInUse = True

        #Sends an error if the email is in use
        if emailInUse == True:
            return HttpResponse("userError")

        #Creating the login
        if emailInUse == False:

            #Checking if the password is long enough
            if len(password1) < 7:
                #Sends error if the password is too short
                return HttpResponse("passError")

            #Hashing the password
            secret = ''.join(random.choice(string.ascii_lowercase) for i in range(12))
            secretHash = str(hashlib.sha256(str.encode(secret)).hexdigest())
            passwordToHash = password1 + secretHash
            passwordHash = str(hashlib.sha256(str.encode(passwordToHash)).hexdigest())

            #Adding the login to the db
            cursor.execute("INSERT INTO dbo.logindb  VALUES ('%s', '%s', '%s');" % (email, secret, passwordHash))
            cnxn.commit()

            request.session["user"] = email
            return HttpResponse("success")

##############Login###########################

#Sends the base html for the login page
def login(request):
    try:
        #Checks if the user is already logged in
        request.session["user"]
        return render(request, "redirect.html", {"redirect": "/"})
    except:
        return render(request, "login.html")

#Checks if a login attempt is valid
def loginCheck(request):
    try:
        request.session["user"]

        #redirect to dashboard
        return HttpResponse("True")

    except:
        if request.method == "GET":
            #Getting the submitted info
            siteUsername = request.GET["username"]
            sitePassword = request.GET["password"]

            #Initiating the SQL session
            cursor.execute("SELECT * from logindb WHERE email = '%s'" % siteUsername)

            #Checks if the login is valid
            allowLogin = False
            for row in cursor:

                #Grabbing hash values
                masterHash = row[2]
                secondaryHash = str(hashlib.sha256(str.encode(row[1])).hexdigest())

                # Encoding the password
                passwordBytes = str.encode(sitePassword + secondaryHash)
                hash = hashlib.sha256(passwordBytes).hexdigest()
                if hash == masterHash:
                    allowLogin = True

            #Setting the session username
            if allowLogin == True:
                request.session["user"] = siteUsername

                #redirect to dashboard
                return HttpResponse("True")
            if allowLogin == False:

                #alert user login info was bad
                return HttpResponse("False")

#Deleted the users login session
def logout(request):
    try:
        del request.session["user"]
    except:
        pass

    return render(request, "redirect.html", {"redirect": "/login/"})


#Home page javascript
def recentInventoryAdditions(request):
    if request.method == 'GET':
        response = request.GET['type']
        if response == 'sold':
            cursor.execute("SELECT item_name,item_retail_price, item_resale_price from itemdb WHERE email = ? AND date_added IS NOT NULL AND item_name IS NOT NULL AND date_posted IS NOT NULL order by date_added", (request.session['user']))
        if response == 'unsold':
            cursor.execute("SELECT item_name,item_retail_price, item_resale_price from itemdb WHERE email = ? AND date_added IS NOT NULL AND item_name IS NOT NULL AND date_posted IS NULL order by date_added", (request.session['user']))
        if response == "all":
            cursor.execute("SELECT item_name,item_retail_price, item_resale_price from itemdb WHERE email = ? AND date_added IS NOT NULL AND item_name IS NOT NULL order by date_added", (request.session['user']))
        recentproducts = cursor.fetchall()
        responsetable = """
<table id="recent-additions-table">
    <thead>
        <tr>
            <th>Product</th>
            <th>Retail Price</th>
            <th>Resale Price</th>
            <th>Projected Profit</th>
        </tr>
    </thead>
    <tbody>"""
        for product in recentproducts:
            name = product[0]
            retail = product[1]
            resale = product[2]
            if retail == None:
                retail = 0
            if resale == None:
                resale = 0
            difference = abs(retail-resale)

            responsetable = responsetable + f"""
        <tr>
            <th>{name}</th>
            <th>${retail}</th>
            <th>${resale}</th>
            <th class="profit-text">${difference}</th>
        </tr>"""
        responsetable = responsetable + """
    </tbody>
</table>"""
        return HttpResponse(responsetable)