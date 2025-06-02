from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from scripts.scrape_jobs import scrape_jobs_with_selenium  # Import the Selenium-based scrape_jobs function
from pymongo import MongoClient

router = APIRouter()

# MongoDB connection
MONGO_URI = "mongodb://mongo:27010"  # Use "mongo" as the hostname in Docker Compose
DATABASE_NAME = "ai_matching"
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Define the request body schema
class ScrapeJobsRequest(BaseModel):
    platform: str
    keyword: str = "Software Engineer"
    location: str = "New York"

@router.post("/scrape-jobs")
async def scrape_jobs_endpoint(request: ScrapeJobsRequest):
    """
    API endpoint to trigger job scraping and update the database.
    Args:
        request (ScrapeJobsRequest): The request body containing platform, keyword, and location.
    Returns:
        dict: The result of the scraping process.
    """
    try:
        # Call the Selenium-based scrape_jobs function
        result = scrape_jobs_with_selenium(
            platform=request.platform, 
            keyword=request.keyword, 
            location=request.location
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Store the scraped jobs in MongoDB
        if "jobs" in result and result["jobs"]:
            db.scraped_jobs.insert_many(result["jobs"])
            print(f"Inserted {len(result['jobs'])} jobs into the database.")

        # Return the scraped jobs as a response
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")