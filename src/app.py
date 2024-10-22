#fastapi api consume data
import os
from dotenv import load_dotenv
import logging
import requests
from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from pydantic import BaseModel, Field, field_validator
import pycountry

#logging config
logging.basicConfig(level=logging.DEBUG)

#Required to load the previously defined environment variables
load_dotenv()

app = FastAPI()

# Pydantic model for request validation
class CityRequest(BaseModel):
    city_name: str = Field(..., min_length=1, max_length=100, description="Name of the city")
    country_code: str = Field(..., min_length=2, max_length=2, pattern=r"^[A-Z]{2}$", description="Country code in ISO 3166-1 alpha-2 format (e.g., 'US', 'MX')")

    # Validator to check if the country_code is a valid ISO 3166-1 alpha-2 code
    @field_validator('country_code', mode='before')
    @classmethod
    def validate_country_code(cls, country_code: str):
        if not pycountry.countries.get(alpha_2=country_code):
            raise ValueError(f"Invalid country code '{country_code}'. Must be a valid ISO 3166-1 alpha-2 code.")
        return country_code

@app.get("/", tags=["home"])
async def root():
    logging.info("Root endpoint accessed")
    return {'status':'ok 👍🐍 '}

@app.get("/current_temperature/")
async def get_current_temp(city: CityRequest = Depends()):
    """
    Get current temperature of the city using OpenWeatherMap API.
    The city and country_code are validated using the CityRequest model.
    """
    api_key = os.environ.get('API_KEY')
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city.city_name},{city.country_code}&appid={api_key}&units=metric'
    response = requests.get(url, timeout=5)

    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        return {'Temperature': temp, 'Description': desc}  
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch temperature data")




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)