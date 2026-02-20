# import flask and its components
from flask import *

#import the pymyscl module, helps create connecting between python flask and mysql database
import pymysql

# Create a flask application and give it a name
app = Flask(__name__)



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





# Run the application
app.run(debug=True)
