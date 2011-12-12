from os.path import abspath, dirname, join
import sys

sys.path.insert(0, join(abspath(dirname(__file__)), '..'))

from plush import Plush

app = Plush(__name__)

@app.get('/')
def index(request):
    request.send('Hello World!')

app.run()
