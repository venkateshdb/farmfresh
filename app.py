"""
Farmfresh
date: 5-1-20
ver: 1
"""

# importing modules

from twilio.rest import Client
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, flash, redirect, url_for, abort, session
from dotenv import load_dotenv
import random
import string
import os, requests
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


@app.route("/")
def main():
    """
    Home page
    """
    print(session)
    return render_template("index.html", get=session.get("logged_in"))


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

        if account_type == "seller":
            get = Seller.query.filter_by(
                phone_num=_num, password=_password).all()
            if get:
                session["logged_in"] = True
                session["user_id"] = get[0].id
                session["username"] = get[0].full_name

                flash("welcome {}".format(session["username"]))
                return redirect(url_for("main"))
            else:
                error = "Invalid"

        elif (account_type == "buyer"):
            get = Buyer.query.filter_by(
                phone_num=_num, password=_password).all()
            if get:
                # if user is present
                session["logged_in"] = "True"
                session["user_id"] = get[0].id
                session["username"] = get[0].full_name
                session["type"] = account_type
                print(session)
                flash("Welcome {}".format(session["username"]))
                return redirect(url_for("main"))

            else:
                error = "Invalid"

        else:
            error = "Pls, choose correct choice"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return "cleared"


def send_otp(otp):
    try:

        message = client.messages.create(
            body="Your OTP For FarmFresh is {0}".format(otp),
            from_="+12132386072",
            to="+918208264232")
        print(message)
        return message.sid
    except requests.exceptions.ConnectionError:
        return None


@app.route("/verify", methods=("GET", "POST"))
def verify():
    error = None

    sess_phone = session.get("phone_num")
    print(sess_phone)
    # get otp entered by user
    if request.method == "POST":
        _otp = request.form['otp']
        print(_otp)
        get = Verify.query.filter_by(phone_num=sess_phone, otp=_otp).all()
        print(get)
        if get:
            flash("Otp successfully verified!!")

            if session.get("type") == "seller":
                Seller.query.filter_by(phone_num=sess_phone).update({
                    "is_verified":
                    1
                })
            elif (session.get("type") == "buyer"):
                Buyer.query.filter_by(phone_num=sess_phone).update({
                    "is_verified":
                    1
                })

            db.session.commit()
            return redirect(url_for("main"))
        else:
            error = "Wrong otp, try again!!"

    return render_template("verify.html", error=error)


@app.route("/add_product")
def add_product():
    return "add"


@app.route("/remove_product")
def remove_product():
    return "rm"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
