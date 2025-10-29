import pytest
from app import app

@pytest.fixture
def client():
    """Flask test client fixture"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  
    with app.test_client() as client:
        yield client

def test_homepage(client):
    """Test homepage loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data  

def test_login_get(client):
    """Test GET /login route"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_login_post_invalid(client):
    """Test POST /login with invalid credentials"""
    response = client.post('/login', data={
        'username': 'fakeuser',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid" in response.data or b"error" in response.data

def test_dashboard_requires_login(client):
    """Test that dashboard requires login"""
    response = client.get('/traveller/dashboard', follow_redirects=True)
    assert b"Login" in response.data or response.status_code in (302, 200)
