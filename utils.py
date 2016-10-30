import glob
import os
import re
from unicodedata import normalize
from flask import current_app as app
from slugify import slugify

# Generates post URLs for Flask-Frozen
def post_url_generator():
    posts_dir = os.path.join(app.config['FLATPAGES_ROOT'], 'posts/*')
    for d in glob.glob(posts_dir):
        m = re.search('(?P<year>20[0-9]{2})$', d)
        year = m.groups()[0]
        for year_dir in glob.glob(os.path.join(d, '*')):
            dir_name = year_dir.split("/")[-1:][0]
            restr = r'(?P<month>[0-9]{2})-(?P<day>[0-9]{2})-(?P<slug>[\w-]+)'
            m = re.search(restr, dir_name)
            if m is not None:
                yield 'post', {
                    'year': year,
                    'month': m.group('month'),
                    'day': m.group('day'),
                    'slug': m.group('slug')
                }

# Generates post asset URLs for Flask-Frozen
def asset_url_generator():
    assets = glob.glob('content/posts/*/*/assets/**/*.*', recursive=True)
    for a in assets:
        print(a)
        if os.path.isfile(a):
            restr = r'(20[0-9]{2})\/([0-9]{2})-([0-9]{2})-(?P<slug>[\w-]+)'
            m = re.search(restr, a)
            groups = m.groups()
            a = re.sub('content/posts/(.*)/assets/', '', a)
            yield 'post_asset', {
                'year': groups[0],
                'month': groups[1],
                'day': groups[2],
                'slug': groups[3],
                'filename': a
            }

# Generates page URLs for Flask-Frozen
def page_url_generator():
    for d in glob.glob(os.path.join(app.config['FLATPAGES_ROOT'], '*.md')):
        m = re.search('(?P<path>[\w-]+)\.md', d)
        if m is not None:
            yield 'page', {'path': m.group('path').replace('.md', '')}


# Gets post filename (sans extension) from slug
def get_post(year, month, day, slug):
    dir_name = '%s-%s-%s' % (month, day, slug)
    path = os.path.join(
        app.config['FLATPAGES_ROOT'], 
        'posts', 
        year,
        dir_name
    )
    f = glob.glob(path)
    if len(f) == 0:
        return None
    return os.path.join(
        f[0].replace(app.config['FLATPAGES_ROOT'] + '/', ''),
        slug
    )

# Gets post path (sans extension) from slug
def get_post_path(year, month, day, slug):
    dir_name = '%s-%s-%s' % (month, day, slug)
    path = os.path.join(
        app.config['FLATPAGES_ROOT'], 
        'posts', 
        year,
        dir_name
    )
    f = glob.glob(path)
    if len(f) == 0:
        return None
    return f[0].replace(app.config['FLATPAGES_ROOT'] + '/', '')


def makeslug(text, delim=u'-'):
    return slugify(text)
