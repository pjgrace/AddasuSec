import falcon
from wsgiref.simple_server import make_server

from API.WebAPI import (
    StartComponentResource,
    CreateComponentResource,
    DeleteComponentResource,
    ConnectResource,
    DisconnectResource
)

app = falcon.App()

app.add_route('/create', CreateComponentResource())
app.add_route('/delete', DeleteComponentResource())
app.add_route('/connect', ConnectResource())
app.add_route('/disconnect', DisconnectResource())
app.add_route('/start', StartComponentResource())

# For gunicorn or waitress:
# gunicorn api.server:app
if __name__ == '__main__':
    with make_server('', 8654, app) as httpd:
        print('Serving on port 8654...')

        # Serve until process is killed
        httpd.serve_forever()