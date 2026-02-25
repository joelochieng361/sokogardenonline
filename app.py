# import flask and its components
from flask import *
import os

#import the pymyscl module, helps create connecting between python flask and mysql database
import pymysql

# Create a flask application and give it a name
app = Flask(__name__)

# Configure the location to where the product images will be saves
app.config["UPLOAD_FOLDER"] = "static/images"



# Below is the sign-up route
@app.route("/api/signup", methods = ["POST"])
def signup():
    if request.method=="POST":
        # Extract the different details entered on the form
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        

        
        # using print function
        #print(username, email, password, phone)
        
        connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenonline")
        
        # create a curson to execute the sql
        cursor = connection.cursor()
        
        #structure an sql to insert the details received from the form
        #The %s is a place holder, They stand in place of actual values
        sql = "INSERT INTO users(username,email,password,phone) VALUES(%s,%s,%s,%s)"
        
        #Create a turple that will hold all the data gotten from the form
        
        data = (username, email, password, phone)
        #By the use of the cursor, execute the sql as you replace the placeholder
        
        cursor.execute(sql, data)
        
        #commit the changes to the database
        connection.commit()
        
        
        return jsonify({"message" : "User registered successfully."})
    
    


# Below is the login/sign in route
@app.route("/api/signin", methods = ["POST"])
def signin():
    if request.method=="POST":
        # Extract the two details entered on the form
        email = request.form["email"]
        password = request.form["password"]
        
        #Create/ Establish a connection to database
        connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenonline")
        
        # Create a cursor
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Structure the sql query that will check whether the  email and password entered are correct
        
        sql = "SELECT * FROM users WHERE email = %s AND password = %s"
        
        # put the received data from the form in a taple
        data = (email, password)
        
        #By use of cursor execute the sql
        cursor.execute(sql, data)
        
        #Check whether there are rows returned and stored on the same variable
        count= cursor.rowcount
        #print(count)
        
        # If there are rows returned, it means the password and email are correct otherwise if they are wrong 
        if count== 0:
            return jsonify({"message" : "login failed"})
        else:
            #There must be a user  so we create a variable that will hold  the details of the users fetched from the database
            user=cursor.fetchone()
            # Return message to the front end
            return jsonify({"message" : "signin route accessed", "user":user})

#Below is a route for adding products
@app.route("/api/add_products", methods = ["POST"])
def Addproducts():
    if request.method == "POST":
        #Extract the data entered from the form
        product_name = request.form["product_name"]
        product_description = request.form["product_description"]
        product_cost = request.form["product_cost"]
        #product photo shall be fetched from files
        product_photos = request.files["product_photos"]
        
        #Extract filename of product
        filename = product_photos.filename
        # by use of the os module (operating system) we can extract the file path where the images is currently saved
        photo_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        
        # print("This is the photo path: ", photo_path)
        # save the product photo image into the new location
        product_photos.save(photo_path)
        
        #Establish connection to database
        connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenonline")
        
        #Create a cursor
        cursor = connection.cursor()
        
        #Create an sql query that will insert products to the database
        
        sql = "INSERT INTO product_details(product_name,product_description,product_cost,product_photos) VALUES(%s, %s, %s, %s)"
        
        #create a turple
        data = (product_name, product_description, product_cost, filename)
        
        #create a cursor to execute the sql
        cursor.execute(sql, data)
        
        connection.commit()
        
        return jsonify({"Message":"product added successfully"})
    

#Below is a route for getting products
@app.route("/api/get_products")
def get_products():
    #create a connection to database
    connection = pymysql.connect(host="localhost", user="root", password="",database="sokogardenonline")
    
    #create a cursor
    cursor = connection.cursor()
    
    #create sql query
    sql = "SELECT * FROM product_details"
    
    # Create a cursor to execute the query
    cursor.execute(sql)
    
    #create a variable that will hold the data
    products = cursor.fetchall()
    
    return jsonify(products)


# Mpesa Payment Route/Endpoint 
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth
 
@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == 'POST':
        amount = request.form['amount']
        phone = request.form['phone']
        # GENERATING THE ACCESS TOKEN
        # create an account on safaricom daraja
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"
 
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
 
        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']
 
        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')
 
        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "1",  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/api/confirmation.php",
            "AccountReference": "account",
            "TransactionDesc": "account"
        }
 
        # POPULAING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }
 
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL
 
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        return jsonify({"message": "Please Complete Payment in Your Phone and we will deliver in minutes"})



# Run the application
app.run(debug=True)
