# Import libraries
import mlflow 
import uvicorn
import pandas as pd
import json
import boto3
import pickle
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile


mlflow.set_tracking_uri("https://mlflow-app-getaround.herokuapp.com/")

description = """
Welcome to the PriceGETAROUND API. This app is made for predict you optimal price for your rental based on your car features, try it out ! 🕹️

## Introduction Endpoint

Here is an endpoint you can try:

* `/`: **GET** request that display a simple default message.

## Machine Learning

This is a Machine Learning endpoint that predict the optimal price for the rentals. Here is the endpoint:

* `/predict`
 
"""

tags_metadata = [
    {
        "name": "Introduction Endpoint",
        "description": "Simple endpoint to try out!",
    },

    {
        "name": "Machine Learning",
        "description": "Prediction Endpoint."
    }
]

app = FastAPI(
    title = "API GETAROUND PROJECT",
    description = description,
    version = "0.1",
    openapi_tags = tags_metadata
)

class PredictionFeatures(BaseModel):
    model_key: str = "Citroën"
    mileage: int = 90401
    engine_power: int = 135
    fuel: str = "diesel"
    paint_color: str = "grey"
    car_type: str = "convertible"
    private_parking_available: bool = True
    has_gps: bool = True
    has_air_conditioning: bool = False
    automatic_car: bool = False
    has_getaround_connect: bool = True
    has_speed_regulator: bool = True
    winter_tires: bool = True

@app.get("/", tags = ["Introduction Endpoint"])
async def index():

    message = "Hello Car owner! This `/` is the most simple and default endpoint for the API`"

    return message

@app.post("/predict", tags = ["Machine Learning"])
async def predict(predictionFeatures: PredictionFeatures):
  
    # Read data 
    df_price = pd.DataFrame(dict(predictionFeatures), index=[0])

    # Log model from mlflow 
    logged_model = 'runs:/e368be4f04734a7eb818869b70f4b743/CarPrice_predictor'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(df_price)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)