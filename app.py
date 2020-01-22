"""
Farmfresh
date: 5-1-20
ver: 1
"""

# importing modules

from twilio.rest import Client
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, flash, redirect, url_for, abort, session, jsonify
from dotenv import load_dotenv
import random
import string
import os, requests, time
import redis

basedir = os.path.abspath(os.path.dirname(__file__))
# app intance and some config
load_dotenv(override=True)

app = Flask(__name__)
app.config.from_object(os.getenv("APP_SETTING"))

# For twilio API client
client = Client(os.getenv("ACCOUNT_SID"), os.getenv("ACCOUNT_TOKEN"))

db = SQLAlchemy(app)
sess = Session(app)

from model import *


##
#       Useful functions
##
def gen():
    return (string.digits)


def id():
    """ generates random otp"""
    key = [random.choice(gen()) for i in range(6)]
    return (int(''.join(key)))


def send_otp(otp):
    """
    function to send otp to a given number
    """
    sess_phone = str(session.get("phone_num"))
    try:
        message = client.messages.create(
            body="Your OTP For FarmFresh is {0}".format(otp),
            from_="+12132386072",
            to="+91" + sess_phone)
        print(message)
        return message.sid
    except requests.exceptions.ConnectionError:
        return None


"""
Some session variables

@logged_in
@user_id
@phone_num
@type(account_type)
@username

"""


@app.route("/")
def main():
    """
    Home page
    """
    return render_template("index.html")


@app.route("/seller", methods=["GET", "POST"])
def seller():
    """
    seller registeration
    """
    error = None
    # getting data from form
    if request.method == "POST":
        full_name = request.form["name"]
        city = request.form["city"]
        state = request.form["state"]
        address = request.form["address"]
        phone = request.form["phone"]
        password = request.form["password"]
        seller_img = request.files["seller_img"]

        session["phone_num"] = phone
        session["type"] = "seller"
        otp = id()

        # Allow seller to add image later
        if not seller_img:
            seller = Seller(
                full_name,
                city,
                state,
                address,
                phone,
                password,
                seller_img_name="",
                is_verified=0)
        else:
            seller = Seller(
                full_name,
                city,
                state,
                address,
                phone,
                password,
                seller_img_name=seller_img.filename,
                is_verified=0)

        print(session, phone)
        verify = Verify(phone, otp)  # add to database
        db.session.add(verify)
        db.session.commit()

        if send_otp(otp) is not None:
            # send a random otp to user number
            db.session.add(seller)
            db.session.commit()
            #commit after verify succesfully
            return redirect(url_for("verify"))
        else:
            error = "Error, WHile sending otp"

    return render_template("seller.html", error=error)


@app.route("/buyer", methods=("GET", "POST"))
def buyer():
    """
    buyer registeration
    """
    error = None
    if request.method == "POST":

        full_name = request.form["name"]
        city = request.form["city"]
        state = request.form["state"]
        address = request.form["address"]
        phone = request.form["phone"]
        password = request.form["password"]
        buyer_img = request.files["buyer_img"]

        session["phone_num"] = phone
        session["type"] = "buyer"
        otp = id()

        if buyer_img == "":
            buyer = Buyer(
                full_name,
                city,
                state,
                address,
                phone,
                password,
                buyer_img_name="",
                is_verified=0)
        else:
            buyer = Buyer(
                full_name,
                city,
                state,
                address,
                phone,
                password,
                buyer_img_name=buyer_img.filename,
                is_verified=0)

        print(session, phone)
        verify = Verify(phone, otp)  # add to database
        db.session.add(verify)
        db.session.commit()

        if send_otp(otp) is not None:
            # send a random otp to user number
            db.session.add(buyer)
            db.session.commit()
            #commit after verify succesfully
            return redirect(url_for("verify"))
        else:
            error = "Error, While sending otp"

    return render_template("buyer.html", error=error)


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    user login
    """
    error = None

    if request.method == "POST":
        _num = request.form["phone_num"]
        _password = request.form["password"]
        account_type = request.form["account_type"]
        print("accounttypee: ",account_type)
        if account_type == "seller":
            get = Seller.query.filter_by(
                phone_num=_num, password=_password).all()
            if get:
                session["logged_in"] = True
                session["user_id"] = get[0].id
                session["username"] = get[0].full_name
                session["type"] = account_type
                session["phone_num"] = _num
                print(session)
                print("ss: ", type(session.get("logged_in")))
                flash("welcome {}".format(session["username"]))
                return redirect(url_for("seller_dashboard"))
            else:
                error = "Invalid Credentials"

        elif(account_type == "buyer"):
            get = Buyer.query.filter_by(
                phone_num=_num, password=_password).all()
            if get:
                # if user is present
                session["logged_in"] = True
                session["user_id"] = get[0].id
                session["username"] = get[0].full_name
                session["type"] = account_type
                session["phone_num"] = _num
                print(session)

                flash("Welcome {}".format(session["username"]))
                return redirect(url_for("buyer_dashboard"))

            else:
                error = "Invalid Credentials"

        else:
            error = "Pls, Choose Correct Choice"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    #TODO : check how to configure session_type to sqlalchemy
    #  and handle .clear on session, as it was removing
    #  date from session table and causing
    #  TypeError: '<=' not supported between instances of 'NoneType' and 'datetime.datetime'
    #  checkout flask_session github repo for this issue
    flash("successfully logout")
    return redirect(url_for("main"))


@app.route("/verify", methods=["GET", "POST"])
def verify():
    error = None

    sess_phone = session.get("phone_num")
    print(sess_phone)
    # get otp entered by user
    if request.method == "POST":
        _otp = request.form['otp']

        # filter by phone number and check entered otp
        get = Verify.query.filter_by(phone_num=sess_phone, otp=_otp).all()

        if get:
            flash("Otp successfully verified!!")

            if session.get("type") == "seller":
                Seller.query.filter_by(phone_num=sess_phone).update({
                    "is_verified":
                    1
                })

                # only for password reset case
                if session.get("new_password") != None:
                    Seller.query.filter_by(phone_num=sess_phone).update({
                        "password":
                        session.get("new_password")
                    })

            elif (session.get("type") == "buyer"):
                Buyer.query.filter_by(phone_num=sess_phone).update({
                    "is_verified":
                    1
                })

                # only for password reset case
                if session.get("new_password") != None:
                    Seller.query.filter_by(phone_num=sess_phone, seller_id=user_id).update({
                        "password":
                        session.get("new_password")
                    })

            db.session.commit()
            return redirect(url_for("login"))
        else:
            error = "Wrong otp, try again!!"

    return render_template("verify.html", error=error, send_to=sess_phone)



@app.route("/seller_dashboard", methods=["GET", "POST"])
def seller_dashboard():
    if(session.get("logged_in") == False and (session.get("type") != "seller")):
        abort(400)
        
   
    # getting session variable
    user_id = session.get("user_id")
    username = session.get("username")
    sess_phone = session.get("phone_num")
    account_type = session.get("type")

    # fetch all those product that this user had posted to sell
    get_selling_products = Product.query.filter_by(seller_id=user_id).all()
    #get = Product.query.join(seller, Product.seller_id).all()
    #print(get_selling_products, user_id, username, sess_phone, account_type)
    #print(get)
    # Storing product details from seller and fetching from database

    return render_template(
        "seller_dashboard.html", products=get_selling_products)


@app.route("/buyer_dashboard", methods=["GET", "POST"])
def buyer_dashboard():
    """
    show products available on marketplace
    """
    if(session.get("logged_in") == False and (session.get("type") != "buyer")):
        abort(400)
   
    # getting session variable
    user_id = session.get("user_id")
    username = session.get("username")
    sess_phone = session.get("phone_num")
    account_type = session.get("type")

    # get all products availabe 
    #get_products = Product.query.join(Seller,Product.seller_id == Seller.id).all()

    get_products = Product.query.all()
    print(get_products)

    return render_template("buyer_dashboard.html", products=get_products)


@app.route("/add_product", methods=["GET","POST"])
def add_product():
    """
    adds product from seller
    """
    if not session.get("logged_in"):
        abort(400)

    # getting session variable
    user_id = session.get("user_id")
    username = session.get("username")
    sess_phone = session.get("phone_num")
    account_type = session.get("type")

    if request.method == "POST":
        """
        Add product to product table
        """
        product_name = request.form["product_name"]
        product_qty = request.form["product_qty"]
        product_price = request.form["product_price"]
        product_date = str(request.form["added_on"])
        category = int(request.form["category"])
        product_img = request.files["product_img"]

        #print(user_id,product_name,product_qty,product_price,added_on,product_img)
        if product_img == "":
            flash("Add a Product Image!!")
            return redirect(url_for(seller_dashboard))
        else:
            # if all ok, add product
            product = Product(product_name, product_qty, product_date, product_price,
                                product_img.filename,seller_id=user_id,category_id=category,seller_name=username,seller_phone=sess_phone)
            print(product)
            db.session.add(product)
            db.session.commit()

        flash("Product Added successfully!!")
        return redirect(url_for("seller_dashboard"))

    return render_template("add_product.html")


@app.route("/remove_product/<int:id>", methods=["POST"])
def remove_product(id):
    """
    remove product
    """
    if not session.get("logged_in"):
        abort(400)

    if request.method == "POST":

        del_product_id = id
        print(del_product_id)

        Product.query.filter_by(product_id=del_product_id).delete()
        db.session.commit()

    return jsonify(status="successfully removed")

@app.route("/resend_otp")
def resend():
    """
    resend otp
    """

    # genereate new otp
    otp = id()
    sess_phone = session.get("phone_num")

    # update previous sent otp to user
    verify = Verify.query.filter_by(phone_num=sess_phone).update({"otp": otp})

    # Now send new otp
    if send_otp(otp) is not None:
        flash("OTP Resend To {}".format(sess_phone))
        db.session.commit()
    else:
        flash("Error, While sending OTP")

    return redirect(url_for("verify"))


@app.route("/forgot_password", methods=["POST", "GET"])
def reset_password():

    otp = id()  #generate an otp
    error = None
    if request.method == "POST":
        phone_num = request.form["phone_num"]
        account_type = request.form["account_type"]
        new_password = request.form["password"]

        session["phone_num"] = phone_num  #add phone_num to session
        session["new_password"] = new_password  # save password to session
        session["type"] = account_type
        # TODO: create a verify fun to check check otp, and return only
        # status of it

        if account_type == "seller":
            try:
                check_if_exist = Seller.query.filter_by(
                    phone_num=phone_num).all()

                if check_if_exist:
                    # if phone number present, then send otp to verify it
                    # add record to database
                    verify = Verify(phone_num, otp)
                    db.session.add(verify)

                    # Now send otp
                    if send_otp(otp) is not None:
                        db.session.commit()
                        return redirect(url_for("verify"))
                    else:
                        error = "Error while sending otp"

            except sqlalchemy.exc.SQLAlchemyError:
                error = "Sorry, Record doesn't exists"

        elif account_type == "buyer":
            try:
                check_if_exist = Seller.query.filter_by(
                    phone_num=phone_num).all()

                if check_if_exist:
                    # if phone number present, then send otp to verify it
                    # add record to database
                    verify = Verify(phone_num, otp)
                    db.session.add(verify)

                    # Now send otp
                    if send_otp(otp) is not None:
                        db.session.commit()
                        return redirect(url_for("verify"))
                    else:
                        error = "Error while sending otp"

            except sqlalchemy.orm.exc:
                error = "Sorry, Record doesn't exists"

    return render_template("forgot_password.html", error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
