from datetime import datetime
import glob
import markdown
import os
import re

from flask import Flask, render_template, abort, send_from_directory
from flask_frozen import Freezer
from flask_flatpages import FlatPages, pygments_style_defs
from werkzeug.contrib.atom import AtomFeed

from config import *
from utils import *

# flask debug option, no reason to change this
DEBUG = True
# directory where flatpages should look for files
FLATPAGES_ROOT = 'content'
# extension that flatpages should try to read and parse
FLATPAGES_EXTENSION = '.md'
# enables triple-backticks for surrounding code blocks
FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', 'fenced_code', 'tables']

freezer = Freezer()
flatpages = FlatPages()

def pygments_css():
    return pygments_style_defs('solarizeddark'), 200, {'Content-Type': 'text/css'}

def home():
    page = flatpages.get_or_404('home')
    return render_template('page.html', page=page)


def page(path):
    page = flatpages.get_or_404(path)
    return render_template('page.html', page=page)

def resume():
    return send_from_directory('./static', 'resume.pdf')

def atom_feed():
    feed = AtomFeed('Recent Blog Postings',
                    feed_url='http://www.brianbove.com/atom.xml',
                    url='http://www.brianbove.com/')
    post_list = post_url_generator()
    for p in post_list:
        post_data = p[1]
        page = flatpages.get(
            get_post(
                post_data['year'],
                post_data['month'],
                post_data['day'],
                post_data['slug']
            )
        )
        path = "%s/%s/%s/%s" % (
            post_data['year'],
            post_data['month'],
            post_data['day'],
            post_data['slug']
        )
        feed.add(
            page.meta['title'],
            content_type='html',
            url='http://www.brianbove.com/blog/%s/' % path,
            author='Brian Bove',
            updated=page.meta['date'],
            published=page.meta['date']
        )
    return feed.get_response()


def blog():
    urls = [p for p in post_url_generator()]
    posts = []
    for i in range(0, len(urls)):
        post_data = urls[i][1]
        page = flatpages.get(
            get_post(
                post_data['year'],
                post_data['month'],
                post_data['day'],
                post_data['slug']
            )
        )
        posts.append({
            'title': page.meta.get('title'),
            'date': page.meta.get('date'),
            'slug': urls[i][1]['slug']
        })
    posts.sort(key=lambda p:p['date'], reverse=True)
    return render_template('blog.html', posts=posts)


def post(year, month, day, slug):
    page = flatpages.get_or_404(get_post(year, month, day, slug))
    template = 'index.html'
    return render_template('post.html', page=page)


def post_asset(year, month, day, slug, filename):
    post_path = get_post_path(year, month, day, slug)
    asset_path = os.path.join(
        'content',
        post_path,
        'assets'
    )
    #print(asset_path)
    return send_from_directory(asset_path, filename)

def create_app():

    app = Flask(__name__)
    app.config.from_object(__name__)
    freezer.init_app(app)
    flatpages.init_app(app)

    app.add_url_rule('/', 'home', home)
    app.add_url_rule('/blog/', 'blog', blog)
    app.add_url_rule('/atom.xml', 'atom_feed', atom_feed)
    app.add_url_rule(
        '/blog/<string:year>/<string:month>/<string:day>/<string:slug>/', 
        'post', 
        post
    )

    app.add_url_rule(
        ('/blog/<string:year>/<string:month>/<string:day>/<string:slug>/' 
         'assets/<path:filename>'),
        'post_asset',
        post_asset
    )
    app.add_url_rule('/<path:path>/', 'page', page)
    app.add_url_rule('/resume.pdf', 'resume', resume)
    app.add_url_rule('/pygments.css', 'pygments_css', pygments_css)

    freezer.register_generator(post_url_generator)
    freezer.register_generator(page_url_generator)
    freezer.register_generator(asset_url_generator)

    return app
