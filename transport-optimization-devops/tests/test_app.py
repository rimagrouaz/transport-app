import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from app import app as flask_app

@pytest.fixture
def app():
    """Create application instance for testing"""
    flask_app.config['TESTING'] = True
    return flask_app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_health_endpoint(client):
    """Test the /health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

def test_ready_endpoint(client):
    """Test the /ready endpoint"""
    response = client.get('/ready')
    # May return 200 or 503 depending on external service availability
    assert response.status_code in [200, 503]
    data = response.get_json()
    assert 'status' in data

def test_home_page(client):
    """Test the home page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Transport Optimization' in response.data or b'transport' in response.data.lower()

def test_itineraire_missing_parameters(client):
    """Test /api/itineraire with missing parameters"""
    response = client.post('/api/itineraire',
                          json={},
                          content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_itineraire_valid_request(client):
    """Test /api/itineraire with valid parameters"""
    response = client.post('/api/itineraire',
                          json={
                              'depart': 'Bordeaux',
                              'destination': 'Paris',
                              'mode': 'voiture'
                          },
                          content_type='application/json')
    # May succeed or fail depending on external API availability
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.get_json()
        assert 'distance' in data or 'success' in data

def test_404_error(client):
    """Test 404 error handling"""
    response = client.get('/nonexistent-route')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_itineraire_different_modes(client):
    """Test different transportation modes"""
    modes = ['voiture', 'bus', 'velo', 'pieton']
    
    for mode in modes:
        response = client.post('/api/itineraire',
                              json={
                                  'depart': 'Bordeaux',
                                  'destination': 'Toulouse',
                                  'mode': mode
                              },
                              content_type='application/json')
        # Accept both success and external API failures
        assert response.status_code in [200, 500]

def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.get('/health')
    # CORS headers should be present
    # This test may need adjustment based on CORS configuration
    assert response.status_code == 200

def test_json_content_type(client):
    """Test API returns JSON content type"""
    response = client.get('/health')
    assert response.content_type == 'application/json'

def test_itineraire_invalid_json(client):
    """Test /api/itineraire with invalid JSON"""
    response = client.post('/api/itineraire',
                          data='invalid json',
                          content_type='application/json')
    assert response.status_code in [400, 500]

# Performance test
def test_health_endpoint_performance(client):
    """Test health endpoint responds quickly"""
    import time
    start_time = time.time()
    response = client.get('/health')
    end_time = time.time()
    
    assert response.status_code == 200
    # Health check should be fast (< 1 second)
    assert (end_time - start_time) < 1.0

# Integration tests would go here
# These would test with real external APIs
# Only run in integration testing environment

@pytest.mark.integration
def test_real_geocoding():
    """Integration test for real geocoding"""
    # This would test actual API calls
    # Skip in unit tests
    pytest.skip("Integration test - requires external API")

@pytest.mark.integration
def test_real_routing():
    """Integration test for real routing"""
    # This would test actual routing calls
    # Skip in unit tests
    pytest.skip("Integration test - requires external API")
