import glob
import markdown
import os

from flask import Flask, render_template, abort
from flask_frozen import Freezer
from utils import Page

DEBUG = True
POST_DIR = os.path.join('content', 'posts')

freezer = Freezer()

class Page:

    def __init__(self, filename):
        f = glob.glob(os.path.join('content', '%s.md' % filename))
        if len(f) == 0:
            abort(404)
        with open(os.path.join('content', '%s.md' % filename)) as fh:
            self.html = markdown.markdown(fh.read(), extensions=['gfm'])


def page(path):
    p = Page(path)
    template = 'index.html'
    return render_template(template, page=p.html)

def post(slug):
    f = glob.glob(os.path.join('content', 'posts', '*%s' % slug))
    p = Page(os.path.join(f[0].replace('content/', ''), slug))
    template = 'index.html'
    return render_template(template, page=p.html)

def create_app():

    app = Flask(__name__)
    app.config.from_object(__name__)
    freezer.init_app(app)
    app.jinja_env.autoescape = False

    app.add_url_rule('/<path:path>/', 'page', page)
    app.add_url_rule('/blog/<string:slug>/', 'slug', post)

    return app
