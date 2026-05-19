"use client";

import { useState } from "react";

import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function Home() {

  const [tripData, setTripData] = useState<any>(null);

  const [loading, setLoading] = useState(false);

  const [source, setSource] = useState("");

  const [destination, setDestination] = useState("");

  const [budget, setBudget] = useState("");

  const [days, setDays] = useState("");

  const [mileage, setMileage] = useState("");

  const generateTrip = async () => {

    try {

      setLoading(true);

      const response = await fetch(
        "http://localhost:8000/trip-plan",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            source,
            destination,
            budget,
            days,
            mileage,
          }),
        }
      );

      const data = await response.json();

      console.log(data);

      setTripData(data);

    } catch (error) {

      console.error("FRONTEND ERROR:", error);

    } finally {

      setLoading(false);

    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-black via-zinc-950 to-black text-white">

      <section className="mx-auto max-w-7xl px-6 py-20">

        <div className="grid items-center gap-10 md:grid-cols-2">

          <div className="space-y-6">

            <h1 className="bg-gradient-to-r from-white to-gray-500 bg-clip-text text-5xl font-extrabold tracking-tight text-transparent md:text-7xl">
              AI Bike Trip Planner
            </h1>

            <p className="max-w-2xl text-lg text-gray-400">
              Plan smarter bike trips with AI agents powered by CrewAI.
              Get routes, fuel estimates, safety advice,
              and AI generated travel insights instantly.
            </p>

          </div>

          <div className="hidden md:block">

            <div className="rounded-3xl border border-gray-800 bg-zinc-950/60 p-8 shadow-2xl backdrop-blur-xl">

              <div className="space-y-5">

                {[
                  "Route Planning Agent",
                  "Fuel Estimation Agent",
                  "Safety Analysis Agent",
                ].map((agent, index) => (

                  <div
                    key={index}
                    className="flex items-center justify-between rounded-xl border border-gray-800 bg-black/40 p-4"
                  >

                    <div className="flex items-center gap-3">

                      <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse"></div>

                      <span>{agent}</span>

                    </div>

                    <span className="text-sm text-green-400">
                      Active
                    </span>

                  </div>

                ))}

              </div>

            </div>

          </div>

        </div>

        <div className="mt-20 grid gap-8 md:grid-cols-2">

          <Card className="border-gray-800 bg-zinc-950/80 text-white shadow-2xl backdrop-blur-xl">

            <CardContent className="space-y-5 p-6">

              <h2 className="text-2xl font-semibold">
                Plan Your Trip
              </h2>

              <Input
                placeholder="Starting Location"
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="border-gray-700 bg-black"
              />

              <Input
                placeholder="Destination"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                className="border-gray-700 bg-black"
              />

              <Input
                placeholder="Budget (₹)"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="border-gray-700 bg-black"
              />

              <Input
                placeholder="Ride Duration (Days)"
                value={days}
                onChange={(e) => setDays(e.target.value)}
                className="border-gray-700 bg-black"
              />

              <Input
                placeholder="Bike Mileage (km/l)"
                value={mileage}
                onChange={(e) => setMileage(e.target.value)}
                className="border-gray-700 bg-black"
              />

              <Button
                onClick={generateTrip}
                className="w-full bg-white text-black hover:bg-gray-300"
              >

                {loading
                  ? "Generating..."
                  : "Generate AI Trip Plan"}

              </Button>

            </CardContent>

          </Card>

          <Card className="border-gray-800 bg-zinc-950/80 text-white shadow-2xl backdrop-blur-xl">

            <CardContent className="space-y-6 p-6">

              <h2 className="text-3xl font-bold">
                AI Generated Trip Plan
              </h2>

              {tripData ? (

                <div className="space-y-6 text-gray-300">

                  <div className="rounded-xl border border-gray-800 bg-black/40 p-5">

                    <h3 className="mb-4 text-xl font-bold text-white">
                      Trip Overview
                    </h3>

                    <ul className="space-y-3 list-disc pl-5">

                      <li>
                        <span className="font-semibold text-white">
                          Route:
                        </span>{" "}
                        {tripData.route}
                      </li>

                      <li>
                        <span className="font-semibold text-white">
                          Distance:
                        </span>{" "}
                        {tripData.distance}
                      </li>

                      <li>
                        <span className="font-semibold text-white">
                          Fuel Estimate:
                        </span>{" "}
                        {tripData.fuel_estimate}
                      </li>

                      <li>
                        <span className="font-semibold text-white">
                          Budget:
                        </span>{" "}
                        ₹{tripData.budget}
                      </li>

                      <li>
                        <span className="font-semibold text-white">
                          Duration:
                        </span>{" "}
                        {tripData.days} Days
                      </li>

                    </ul>

                  </div>

                  <div className="rounded-xl border border-gray-800 bg-black/40 p-5">

                    <h3 className="mb-4 text-xl font-bold text-white">
                      Recommended Stops
                    </h3>

                    <ul className="space-y-2 list-disc pl-5">

                      {tripData.best_stops?.map(
                        (stop: string, index: number) => (

                          <li key={index}>
                            {stop}
                          </li>

                        )
                      )}

                    </ul>

                  </div>

                  <div className="rounded-xl border border-gray-800 bg-black/40 p-5">

                    <h3 className="mb-4 text-xl font-bold text-white">
                      Safety Advice
                    </h3>

                    <ul className="list-disc pl-5">

                      <li>
                        {tripData.safety_tip}
                      </li>

                    </ul>

                  </div>

                  <div className="rounded-xl border border-gray-800 bg-black/40 p-5">

                    <h3 className="mb-4 text-xl font-bold text-white">
                      CrewAI Analysis
                    </h3>

                    <div className="whitespace-pre-wrap leading-8 text-gray-300">

                      {tripData.ai_analysis}

                    </div>

                  </div>

                </div>

              ) : (

                <p className="text-gray-500">
                  Your AI trip plan will appear here...
                </p>

              )}

            </CardContent>

          </Card>

        </div>

      </section>

    </main>
  );
}