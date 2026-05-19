import os
import requests

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

load_dotenv()

# API KEYS

ORS_API_KEY = os.getenv("ORS_API_KEY")

# OPENROUTER MODEL

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
    model="meta-llama/llama-3.1-8b-instruct",
    temperature=0.7
)

# FASTAPI APP

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

# MAIN API

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

    # COST ESTIMATION

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

    # ROUTE AGENT

    route_agent = Agent(
        role="Motorcycle Route Expert",
        goal="Provide route and riding guidance",
        backstory="Expert in Indian motorcycle touring routes",
        llm=llm,
        verbose=False
    )

    # ITINERARY AGENT

    itinerary_agent = Agent(
        role="Travel Itinerary Planner",
        goal="Create destination travel itineraries",
        backstory="Expert in tourism and destination experiences",
        llm=llm,
        verbose=False
    )

    # ROUTE TASK

    route_task = Task(
        description=f"""
        Analyze this motorcycle route.

        Source:
        {trip.source}

        Destination:
        {trip.destination}

        Distance:
        {distance_km} km

        Provide:
        - best riding timing
        - road conditions
        - break suggestions
        - riding strategy
        - weather advice

        Keep response concise.
        """,
        expected_output="Motorcycle route guidance",
        agent=route_agent
    )

    # DESTINATION ITINERARY TASK

    itinerary_task = Task(
        description=f"""
        Create a STRICTLY {trip.days}-day destination itinerary.

        Trip:
        {trip.source} to {trip.destination}

        IMPORTANT:
        - MUST contain EXACTLY {trip.days} days
        - Do NOT create extra days

        Focus on:
        - tourist attractions
        - beaches
        - cafes
        - food places
        - photography spots
        - local experiences
        - scenic locations
        - nightlife
        - relaxing activities

        Avoid focusing too much on riding schedules.

        Keep itinerary clean and practical.
        """,
        expected_output=f"Exactly {trip.days}-day itinerary",
        agent=itinerary_agent
    )

    # CREW

    crew = Crew(
        agents=[
            route_agent,
            itinerary_agent
        ],
        tasks=[
            route_task,
            itinerary_task
        ],
        verbose=False
    )

    result = crew.kickoff()

    final_result = str(result)

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
            "Popular Food Stop",
            "Scenic Photography Point",
            "Fuel & Rest Stop"
        ],

        "safety_tip": "Avoid night riding and take breaks every 2-3 hours.",

        "ai_analysis": final_result
    }