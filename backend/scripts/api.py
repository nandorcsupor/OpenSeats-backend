from fastapi import FastAPI, status
import psycopg2
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from .deploy_match import deploy_match, convert_to_timestamp

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

venue_config = (
    ["Gate A", "Gate B", "Gate C", "Gate D"],
    ["Section A", "Section B", "Section C", "Section D"],
    [10, 10, 10, 10],
    [100, 100, 100, 100],
    [4, 3, 2, 1]  # In USD
)

@app.post("/create-match")
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

    if address:
        # Only if the ticket deployment was successful and an address is returned

        conn = psycopg2.connect(
            host="localhost",
            database="nandor",
            user="nandor",
            password="password"
        )

        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tickets (ticket_address, max_tickets, ticket_date, match_name) "
                    "VALUES (%s, %s, %s, %s)",
                    (address, match_data['max_tickets'], match_data['date'], match_data['token_name'])
                )
    
        status_code = status.HTTP_200_OK
        message = f"Successfully deployed match smart contract at: {address}"

        return {"message": message, "status_code": status_code}

    error_code = status.HTTP_503_SERVICE_UNAVAILABLE
    message = f"Some Error in the Backend"

    return {"message": message, "status_code": error_code}

@app.get("/get-matches")
def get_matches():
    conn = psycopg2.connect(
        host="localhost",
        database="nandor",
        user="nandor",
        password="password"
    )

    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tickets")
            rows = cursor.fetchall()

    matches = []
    for row in rows:
        match = {
            "ticket_address": row[0],
            "max_tickets": row[1],
            "ticket_date": row[2],
            "match_name": row[3]
        }
        matches.append(match)

    return matches


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
