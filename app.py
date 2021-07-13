from apig_wsgi import make_lambda_handler
from bottle import default_app, template, static_file, route

app = default_app()

lambda_handler = make_lambda_handler(app)


@route('/static/<path:path>')
def static(path):
    return static_file(path, "./static")


@route('/<path:re:.*>')
def other_paths(path):
    return template('index.html')


@route('/<path:re:.*>', method='POST')
def other_paths(path):
    return template('index.html')
