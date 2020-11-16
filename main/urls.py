from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home, name="itemizer"),

    #Logout
    path('logout/', views.logout, name="Logout Function"),

    #Signup
    path('signup/', views.signup, name="Signup Page"),
    path('signupcreate/', views.signupCreate, name="Signup Creation Function"),

    #Account
    path('settings/', views.settings, name="User Settings"),
    path('settings/update/', views.updateSettings, name="Updates the User Settings"),


    #Login
    path('login/', views.login, name="Login Page"),
    path('logincheck/', views.loginCheck, name="Login Check Function"),


    #Inventory
    path('inventory/', views.inventory, name="Inventory Page"),
    path('table/', views.buildInventoryTable, name="Gets the table"),
    path('additem/', views.addItem, name="Adds item to the inventory"),
    path('additem/submit/', views.addItemToDB, name="Adds the item to the inventory db"),

    path('edit/', views.edit, name="Allows the user to edit an item in the db"),
    path('edit/images/', views.editItemImages, name="Sends the images of the item"),
    path('edit/submit/', views.saveEdits, name="Saves the users edits for an item in db"),

    #Listings
    path('listings/', views.listings, name="Adds the item to the inventory db"),

    #Homepage Javascript
        path('recentinventory/', views.recentInventoryAdditions, name="Retrieves user most recent inventory additions"),

]