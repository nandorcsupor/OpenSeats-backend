import requests

# Base URL for the API
BASE_URL = 'http://localhost:8000'

# Endpoint URL for creating a match
CREATE_MATCH_URL = f'{BASE_URL}/create-match'

# Test data for creating a match
match_data = {
    'max_tickets': 10000,
    'tokenName': 'Ticket',
    'tokenSymbol': 'TK',
    'gate': 'Gate A',
    'section': 'Section A',
    'row': 5,
    'seat': 69,
    'category': 2
}

def test_create_match():
    response = requests.post(CREATE_MATCH_URL, json=match_data)
    assert response.status_code == 200
    assert response.json() == {'message': 'Match created successfully'}
    print('Create match test passed.')

# Run the test
test_create_match()
