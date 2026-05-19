import os
import requests

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from openai import OpenAI

load_dotenv()

# API KEYS

ORS_API_KEY = os.getenv("ORS_API_KEY")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# FASTAPI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REQUEST MODEL

class TripRequest(BaseModel):
    source: str
    destination: str
    budget: str
    days: str
    mileage: str

# HOME ROUTE

@app.get("/")
def home():
    return {
        "message": "AI Bike Trip Planner Backend Running"
    }

# GET COORDINATES

def get_coordinates(place_name):

    url = "https://api.openrouteservice.org/geocode/search"

    headers = {
        "Authorization": ORS_API_KEY
    }

    params = {
        "text": f"{place_name}, India",
        "size": 1
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    data = response.json()

    coordinates = data["features"][0]["geometry"]["coordinates"]

    return coordinates

# TRIP PLAN API

@app.post("/trip-plan")
def generate_trip_plan(trip: TripRequest):

    # COORDINATES

    source_coords = get_coordinates(trip.source)

    destination_coords = get_coordinates(trip.destination)

    # ROUTE API

    route_url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            source_coords,
            destination_coords
        ]
    }

    response = requests.post(
        route_url,
        json=body,
        headers=headers
    )

    route_data = response.json()

    distance_meters = route_data["routes"][0]["summary"]["distance"]

    distance_km = round(distance_meters / 1000)

    # COSTS

    petrol_price = 105

    fuel_needed = distance_km / int(trip.mileage)

    fuel_estimate = round(fuel_needed * petrol_price)

    food_cost = int(trip.days) * 500

    hotel_cost = int(trip.days) * 1500

    misc_cost = 1000

    total_trip_cost = (
        fuel_estimate
        + food_cost
        + hotel_cost
        + misc_cost
    )

    # AI ITINERARY

    prompt = f"""
    Create a STRICT {trip.days}-day travel itinerary.

    Trip:
    {trip.source} to {trip.destination}

    Distance:
    {distance_km} km

    Focus on:
    - tourist places
    - cafes
    - beaches
    - scenic locations
    - local food
    - nightlife
    - photography spots
    - relaxing activities

    Keep it concise and practical.
    """

    completion = client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    ai_result = completion.choices[0].message.content

    # RESPONSE

    return {

        "route": f"{trip.source} → {trip.destination}",

        "distance": f"{distance_km} km",

        "fuel_estimate": f"₹{fuel_estimate}",

        "food_cost": f"₹{food_cost}",

        "hotel_cost": f"₹{hotel_cost}",

        "misc_cost": f"₹{misc_cost}",

        "total_trip_cost": f"₹{total_trip_cost}",

        "budget": trip.budget,

        "days": trip.days,

        "best_stops": [
            "Scenic Stop",
            "Popular Food Stop",
            "Fuel & Rest Stop"
        ],

        "safety_tip": "Avoid night riding and rest every 2-3 hours.",

        "ai_analysis": ai_result
    }