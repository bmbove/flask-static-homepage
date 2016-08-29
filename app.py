import glob
import markdown
import os
import re

from flask import Flask, render_template, abort
from flask_frozen import Freezer
from flask_flatpages import FlatPages

DEBUG = True
POST_DIR = os.path.join('content', 'posts')
FLATPAGES_ROOT = 'content'
FLATPAGES_EXTENSION = '.md'
FLATPAGES_MARKDOWN_EXTENSIONS = ['gfm']

freezer = Freezer()
flatpages = FlatPages()

# Generates post URLs for Flask-Frozen
def post_url_generator():
    for d in glob.glob(os.path.join(FLATPAGES_ROOT, 'posts/*')):
        match = re.search('[0-9]+(?P<slug>.*)', d)
        m = re.search('[0-9]+-[0-9]+-[0-9]+-(?P<slug>[\w-]+)', d)
        if m is not None:
            yield 'post', {'slug': m.group('slug')}


# Generates page URLs for Flask-Frozen
def page_url_generator():
    for d in glob.glob(os.path.join(FLATPAGES_ROOT, '*.md')):
        m = re.search('(?P<path>[\w-]+)\.md', d)
        if m is not None:
            yield 'page', {'path': m.group('path').replace('.md', '')}

def home():
    page = flatpages.get_or_404('home')
    return render_template('page.html', page=page)

def page(path):
    page = flatpages.get_or_404(path)
    return render_template('page.html', page=page)


def blog():
    posts = [p for p in post_url_generator()]
    return render_template('blog.html', posts=posts)


def post(slug):
    f = glob.glob(
        os.path.join(FLATPAGES_ROOT, 'posts', '*%s' % slug)
    )
    if len(f) == 0:
        abort(404)
    page = flatpages.get_or_404(
        os.path.join(f[0].replace(FLATPAGES_ROOT + '/', ''), slug)
    )
    template = 'index.html'
    return render_template('post.html', page=page)


def create_app():

    app = Flask(__name__)
    app.config.from_object(__name__)
    freezer.init_app(app)
    flatpages.init_app(app)

    app.add_url_rule('/', 'home', home)
    app.add_url_rule('/blog/', 'blog', blog)
    app.add_url_rule('/blog/<string:slug>/', 'post', post)
    app.add_url_rule('/<path:path>/', 'page', page)

    freezer.register_generator(post_url_generator)
    freezer.register_generator(page_url_generator)

    return app
