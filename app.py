from apig_wsgi import make_lambda_handler
from bottle import default_app, template, static_file, route, response

app = default_app()

lambda_handler = make_lambda_handler(app)


def service_unavailable():
    response.status = 503
    response.body = template('index.html')
    return response


@route('/favicon.ico')
def favicon():
    return static_file("favicon.ico", "./static")


@route('/static/<path:path>')
def static(path):
    return static_file(path, "./static")


@route('/<path:re:.*>')
def other_paths(path):
    return service_unavailable()


@route('/<path:re:.*>', method='POST')
def other_paths(path):
    return service_unavailable()
