import pytest
from application import application

@pytest.fixture
def client():
    application.config['TESTING'] = True
    with application.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health check endpoint"""
    rv = client.get('/health')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['status'] == 'healthy'

def test_home_page(client):
    """Test home page loads"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'ScalableFin' in rv.data

def test_loan_page(client):
    """Test loan calculator page"""
    rv = client.get('/loan')
    assert rv.status_code == 200
    assert b'Loan Calculator' in rv.data

def test_insurance_page(client):
    """Test insurance calculator page"""
    rv = client.get('/insurance')
    assert rv.status_code == 200
    assert b'Insurance Calculator' in rv.data

def test_tax_page(client):
    """Test tax calculator page"""
    rv = client.get('/tax')
    assert rv.status_code == 200
    assert b'Tax Calculator' in rv.data
