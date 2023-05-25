from fastapi import FastAPI, status
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from scripts.deploy_match import convert_to_timestamp, deploy_match


app = FastAPI()

# Set CORS configurations
origins = [
    "http://localhost:3000",
    # Add other allowed origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VenueConfig(BaseModel):
    pass


venue_config = (
        ["Gate A", "Gate B", "Gate C", "Gate D"],
        ["Section A", "Section B", "Section C", "Section D"],
        [10, 10, 10, 10],
        [100, 100, 100, 100],
        [4, 3, 2, 1]  # In USD
    )

class MatchCreateRequest(BaseModel):
    max_tickets: int
    token_name: str
    token_symbol: str
    gate: str
    section: str
    row: int
    seat: int
    category: int

@app.post('/create-match')
def create_match(match_data: dict):
    if not match_data:
        status_code = status.HTTP_204_NO_CONTENT
        message = "Request body is empty"
        return {"message": message, "status_code": status_code}

    address = deploy_match(
        max_tickets=match_data['max_tickets'], 
        token_name=match_data['token_name'], 
        token_symbol=match_data['token_symbol'],
        venue_config=venue_config,
        date=convert_to_timestamp(match_data['date'])
    )

    status_code = status.HTTP_200_OK
    message = f"Successfully deployed match smart contract at: {address}"

    return {"message": message, "status_code": status_code}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
