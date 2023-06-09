from fastapi import FastAPI, status
import psycopg2
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from .deploy_match import bind_ticket_service, deploy_match, convert_to_timestamp, mint_ticket

app = FastAPI()

# Set CORS configurations
origins = [
    "http://localhost:3000",
    # Add other allowed origins here
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# TODO - Get rid of hardcoded venue config!
# TODO - Until fixed - use these when minting tickets!
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


@app.get("/get-binded-tickets")
def get_matches():
    conn = psycopg2.connect(
        host="localhost",
        database="nandor",
        user="nandor",
        password="password"
    )

    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM binded_tickets")
            rows = cursor.fetchall()

    tickets = []
    for row in rows:
        ticket = {
            "contract_address": row[0],
            "full_name": row[1],
            "email": row[2],
            "tokenid": row[3]
        }
        tickets.append(ticket)

    return tickets


@app.post("/buy-ticket")
def buy_ticket(buy_ticket_data: dict):
    
    ticket = mint_ticket(
        ticket_contract_address=buy_ticket_data['ticket_contract_address'],
        gate=buy_ticket_data['gate'],
        section=buy_ticket_data['section'],
        row=buy_ticket_data['row'],
        seat=buy_ticket_data['seat'],
        category=buy_ticket_data['category']
    )

    print('TICKET IN API:', ticket)

    # Only if the ticket NFT minting was successful
    # Insert NFT into our database - so we can identify the holder later.

    if ticket:

        conn = psycopg2.connect(
            host="localhost",
            database="nandor",
            user="nandor",
            password="password"
        )

        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO ticket_nfts (transaction_hash, gate, section, row, seat, category, token_id, email, full_name) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (str(ticket['transaction_hash']),
                    buy_ticket_data['gate'], 
                    buy_ticket_data['section'], 
                    buy_ticket_data['row'],
                    buy_ticket_data['seat'],
                    buy_ticket_data['category'],
                    ticket['token_id'],
                    buy_ticket_data['full_name'],
                    buy_ticket_data['email']
                    )
                )

        status_code = status.HTTP_200_OK
        message = f"Successfully bought an NFT Ticket!: {ticket}"

        return {"message": message, "status_code": status_code}
    print('ERRROR IN API')
    return {"message": "Error!"}


@app.post("/bind-ticket")
def bind_ticket(bind_ticket_data: dict):
    ticket_contract_address= bind_ticket_data['ticket_contract_address']
    token_id= bind_ticket_data['token_id']
    email = bind_ticket_data['email']
    full_name = bind_ticket_data['full_name']


    bind_ticket_response = bind_ticket_service(
        ticket_contract_address,
        token_id
    )

    if bind_ticket_response:
        conn = psycopg2.connect(
            host="localhost",
            database="nandor",
            user="nandor",
            password="password"
        )

        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO binded_tickets (contract_address, full_name, email, tokenid) "
                    "VALUES (%s, %s, %s, %s)",
                    (str(ticket_contract_address),
                    full_name,
                    email,
                    token_id
                    )
                )

        status_code = status.HTTP_200_OK
        message = f"Successfully binded ticket:{bind_ticket_response}"
        return {"message": message, "status_code": status_code}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
