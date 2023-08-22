from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel
# from .restapis import related methods
from .restapis import get_request, get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id_from_cf, post_request

from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/registration.html', context)
    else:
        return render(request, 'djangoapp/registration.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/2514ae06-9a30-4f59-8e65-db737bb8dcf4/dealership-package/get-dealership.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name

        context = {
            "dealership_list": dealerships
        }

        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/2514ae06-9a30-4f59-8e65-db737bb8dcf4/dealership-package/get-review.json"
        # Get dealers from the URL
        dealerships = get_dealer_reviews_from_cf(url, dealer_id)
        # Concat all dealer's short name
        context = {
            "dealership_list": dealerships,
            "dealer_id":dealer_id
        }
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)

    
# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    #if request.user.is_authenticated:
        if request.method == "GET":
            url = "https://us-south.functions.appdomain.cloud/api/v1/web/2514ae06-9a30-4f59-8e65-db737bb8dcf4/dealership-package/get-dealership-by-id.json"
            dealer = get_dealer_by_id_from_cf(url, dealer_id)
            cars = CarModel.objects.all()
            context = {
                "cars": cars,
                "dealer": dealer,
                "dealer_id":dealer_id
            }
            print(dealer)

            return render(request, 'djangoapp/add_review.html', context)
        if request.method == "POST":
            url = "https://us-south.functions.appdomain.cloud/api/v1/web/2514ae06-9a30-4f59-8e65-db737bb8dcf4/dealership-package/post-review"
            post_req = request.POST
            car_id = post_req["car"]
            car = CarModel.objects.get(pk=car_id)
            review = dict()
            review["name"] = request.user.first_name + " " + request.user.last_name
            review["dealership"] = dealer_id
            review["review"] = post_req["content"]
            review["purchase"] = post_req["purchasecheck"]
            if review["purchase"]:
                review["purchase_date"] = post_req["purchasedate"]
            review["car_make"] = car.carMake.name
            review["car_model"] = car.name
            review["car_year"] = int(car.year.strftime("%Y"))
            json_payload = {"review" : review}
            post_request(url, json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
    #else:
        #return redirect("/djangoapp/login")