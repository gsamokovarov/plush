import tornado.web
from tornado.ioloop import IOLoop

class Index(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello World!')

app = tornado.web.Application([('/', Index)])
app.listen(8088)

IOLoop.instance().start()
