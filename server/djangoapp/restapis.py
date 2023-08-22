import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url,api_key=None, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if api_key:
             # Basic authentication GET
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)

    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    #print(response.text)
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(f"POST to {url}")
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print("An error occurred while making POST request. ")
    status_code = response.status_code
    print(f"With status {status_code}")

    return response

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        print("WORKING")
        # Get the row list in JSON as dealers
        dealers = json_result["result"]
        # For each dealer object
        

        for dealer in dealers:
            # Get its content in `doc` object
            # dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
            print(dealer["zip"])
    
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_id_from_cf(url, dealer_id):
    #print("this is id",dealer_id)
    json_result = get_request(url, id=dealer_id)
    
    #print('json_result from line 54',json_result)

    if json_result:
        
        dealers = json_result
        #print("this is delears" ,dealers)
        dealer_docs = dealers["body"]["data"]["docs"]
        for dealer_doc in dealer_docs:
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
    return dealer_obj

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, id=dealer_id)
    if json_result:
        print("WORKING")
        #print(json_result)
        # Get the row list in JSON as dealers
        reviews = json_result["body"]["data"]["docs"]
        # For each dealer object
        

        for review_item in reviews:
            # Get its content in `doc` object
            # dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            print(review_item)
            review_obj = DealerReview( dealership=review_item["dealership"], name=review_item["name"], 
                            purchase=review_item["purchase"],review=review_item["review"], purchase_date=review_item["purchase_date"], 
                            car_make=review_item["car_make"], car_model=review_item["car_model"], car_year=review_item["car_year"], 
                            thing_id=10, sentiment=analyze_review_sentiments(review_item["review"]))
            results.append(review_obj)
    print(results)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(review):
    json_result = get_request(url="https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/75c527da-5d56-4f32-8840-6d2d13387a71/v1/analyze", 
                        api_key="1POkSgBkeUgYQZGOTR0Kh49Y_mVGK6vozifWoscX3NFC",
                        text=review,
                        version="2022-04-07",
                        features="sentiment")
    try:
        return json_result["sentiment"]["document"]["label"]
    except KeyError:
        return 'neutral'


