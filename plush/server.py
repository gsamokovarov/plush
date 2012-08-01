from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


class Server(object):
    '''
    Wrapper around the tornado server.
    '''

    DEFAULT_HTTP_PORT = 8088

    http_server_class = HTTPServer
    io_loop_class = IOLoop

    def __init__(self, backend, io_loop):
        self.backend = backend
        self.io_loop = io_loop or self.io_loop_class.instance()

    def serve(self, **options):
        server = self.http_server_class(self.backend)
        server.listen(options.get('port', 8088))

        if options.get('show_heading', True):
            self.show_heading()

        self.io_loop.start()

    def show_heading(self):
        print '''\
 ______ _____   _______ _______ _______
|   __ \     |_|   |   |     __|   |   |
|    __/       |   |   |__     |       |
|___|  |_______|_______|_______|___|___|
'''
