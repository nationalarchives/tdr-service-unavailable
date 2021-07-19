from app import lambda_handler


def test_root_returns_html():
    event = {
        "httpMethod": "GET",
        "path": "/"
    }
    assert "Sorry, the service is unavailable" in lambda_handler(event, None)['body']


def test_url_with_path_returns_html():
    event = {
        "httpMethod": "GET",
        "path": "/a/different/path"
    }

    response = lambda_handler(event, None)
    assert "Sorry, the service is unavailable" in response['body']
    assert 503 == response['statusCode']


def test_static_request_returns_static_file():
    event = {
        "httpMethod": "GET",
        "path": "/static/tna-horizontal-white-logo.svg"
    }

    response = lambda_handler(event, None)
    assert "<svg version=" in response['body']
    assert response['statusCode'] == 200


def test_post_with_path_returns_html():
    event = {
        "httpMethod": "POST",
        "path": "/a/different/path"
    }

    response = lambda_handler(event, None)
    assert "Sorry, the service is unavailable" in response['body']
    assert response['statusCode'] == 503


def test_root_post_returns_html():
    event = {
        "httpMethod": "POST",
        "path": "/"
    }
    response = lambda_handler(event, None)
    assert "Sorry, the service is unavailable" in response['body']
    assert response['statusCode'] == 503
