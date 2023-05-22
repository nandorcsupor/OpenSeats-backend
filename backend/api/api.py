from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

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

class MatchCreateRequest(BaseModel):
    max_tickets: int
    tokenName: str
    tokenSymbol: str
    gate: str
    section: str
    row: int
    seat: int
    category: int

@app.post('/create-match')
def create_match(match_data: dict):
    print('MATCH DATA:', match_data)
    # Extract the necessary fields from the request body
    # max_tickets = match_data.max_tickets
    # tokenName = match_data.tokenName
    # tokenSymbol = match_data.tokenSymbol
    # gate = match_data.gate
    # section = match_data.section
    # row = match_data.row
    # seat = match_data.seat
    # category = match_data.category

    # Rest of your Brownie code...
    # deploy_ticket(max_tickets, tokenName, tokenSymbol, gate, section, row, seat, category)

    return {'message': 'Match created successfully'}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
