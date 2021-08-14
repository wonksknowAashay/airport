from flask import *
from flask_pymongo import PyMongo
import random
from datetime import datetime

myApp = Flask(__name__)
myApp.debug = True
myApp.secret_key = "bheem"

myApp.config[
    "MONGO_URI"] = "mongodb+srv://vedajanga:82601vut@cluster0.lqzsq.mongodb.net/projects?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
mongo = PyMongo(myApp)


def secureroute():
    if "login" in session:
        if session["login"] == False:
            flash("You need to login to continue.", "danger")
            return False
    else:
        flash("You need to login to continue.", "danger")
        return False


@myApp.route("/")
def index():
    return render_template("home.html")


@myApp.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin_login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        if username == "vedajanga":
            if password == "34679600":
                session["login"] = True
                return redirect("/admin_dashboard")
            else:
                flash("Incorrect password", "danger")
                return redirect("/admin_login")
        else:
            flash("Incorrect username", "danger")
            return redirect("/admin_login")


@myApp.route("/admin_dashboard")
def admin_dashboard():
    result = secureroute()
    if result == False:
        return redirect("/admin_login")
    else:
        return render_template("admin_dashboard.html")


@myApp.route("/logout")
def logout():
    session["login"] = False
    return redirect("/")


@myApp.route("/checkfinances")
def checkfinances():
    return render_template("checkfinances.html")


@myApp.route("/createflight", methods=["GET", "POST"])
def createflight():
    if request.method == "GET":
        return render_template("createflight.html")
    else:
        airline = request.form["airline"]
        ids=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","1","2","3","4","5","6","7","8","9","0"]
        idnumber = "".join(random.sample(ids,10))
        departuretime = request.form["departuretime"]
        destination = request.form["destination"]
        departuredate = request.form["departuredate"]
        source = request.form["source"]
        capacity = request.form["capacity"]
        type = request.form["type"]
        departureday = request.form["departureday"]

        mongo.db.flights.insert_one(
            {"airline": airline, "idnumber": idnumber, "departuretime": departuretime, "destination": destination,
             "departuredate": departuredate, "source": source, "capacity": capacity, "type": type, "departureday": departureday})
        flash("Flight created successfully.", "success")
        return redirect("/admin_dashboard")


@myApp.route("/deleteflight", methods=["GET", "POST"])
def deleteflight():
    if request.method == "GET":
        return render_template("deleteflight.html")
    else:
        idnumber = request.form["idnumber"]
        mongo.db.flights.delete_one({"idnumber": idnumber})
        flash('Flight deleted.', 'alert alert-danger')
        return redirect("/admin_dashboard")


@myApp.route("/updateflight",methods=["GET","POST"])
def updateflight():
    if request.method=="GET":
        flightnumber = request.args["number"]
        flight = mongo.db.flights.find_one({"idnumber":flightnumber})
        return render_template("updateflight.html",flight=flight)
    else:
        flightnumber=request.form["idnumber"]
        airline = request.form["airline"]
        departuretime = request.form["departuretime"]
        destination = request.form["destination"]
        departuredate = request.form["departuredate"]
        source = request.form["source"]
        capacity = request.form["capacity"]
        mongo.db.flights.update_one({"idnumber":flightnumber},{"$set":{"airline": airline, "departuretime": departuretime, "destination": destination,
             "departuredate": departuredate, "source": source, "capacity": capacity}})
        flash("Flight information updated successfully.","success")
        return redirect("/seeallflights")


@myApp.route("/bookflight")
def bookflight():

    return render_template("bookflight.html")

@myApp.route("/seeallflights")
def seeflights():
    data = mongo.db.flights.find()
    flights = []
    for x in data:
        flights.append(x)
    return render_template("seeallflights.html", flights=flights)


@myApp.route("/public",methods=["GET","POST","PUT"])
def public():
    if request.method=="GET":
        return render_template("public.html")
    elif request.method=="POST":
        date=request.form["departuredate"]
        source=request.form["source"]
        destination=request.form["destination"]

        found=mongo.db.flights.find({"departuredate":date,"source":source,"destination":destination})
        flights=[]
        for x in found:
            flights.append(x)
        return render_template("seesearchresult.html",flights=flights)
    elif request.method=="PUT":
        passengers=request.form["passengers"]
        flight_id=request.form["flight_id"]

        flightdetails=mongo.db.flights.find_one({"idnumber":flight_id})
        capacity=flightdetails["capacity"]

        capacity=capacity-passengers
        if capacity<0:
            flash("This flight  has exceeded the passenger limit.",'alert alert-danger')
            return redirect("/public")
        mongo.db.flights.update_one({"idnumber":flight_id},{"capacity":capacity})
        return redirect("/public")



if __name__ == "__main__":
    myApp.run()
