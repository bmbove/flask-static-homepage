import glob
import os
import re
from unicodedata import normalize
from flask import current_app as app

# Generates post URLs for Flask-Frozen
def post_url_generator():
    for d in glob.glob(os.path.join(app.config['FLATPAGES_ROOT'], 'posts/*')):
        #match = re.search('[0-9]+(?P<slug>.*)', d)
        m = re.search('[0-9]+-[0-9]+-[0-9]+-(?P<slug>[\w-]+)', d)
        if m is not None:
            yield 'post', {'slug': m.group('slug')}

# Generates post asset URLs for Flask-Frozen
def asset_url_generator():
    assets = glob.glob('content/posts/*/assets/**/*.*', recursive=True)
    for a in assets:
        if os.path.isfile(a):
            m = re.search('[0-9]+-[0-9]+-[0-9]+-(?P<slug>[\w-]+)', a)
            a = re.sub('content/posts/(.*)/assets/', '', a)
            yield 'post_asset', {
                'slug': m.group('slug'),
                'filename': a
            }

# Generates page URLs for Flask-Frozen
def page_url_generator():
    for d in glob.glob(os.path.join(app.config['FLATPAGES_ROOT'], '*.md')):
        m = re.search('(?P<path>[\w-]+)\.md', d)
        if m is not None:
            yield 'page', {'path': m.group('path').replace('.md', '')}


# Gets post filename (sans extension) from slug
def get_post_from_slug(slug):
    f = glob.glob(
        os.path.join(app.config['FLATPAGES_ROOT'], 'posts', '*%s' % slug)
    )
    if len(f) == 0:
        return None
    return os.path.join(
        f[0].replace(app.config['FLATPAGES_ROOT'] + '/', ''),
        slug
    )

# Gets post path (sans extension) from slug
def get_path_from_slug(slug):
    f = glob.glob(
        os.path.join(app.config['FLATPAGES_ROOT'], 'posts', '*%s' % slug)
    )
    if len(f) == 0:
        return None
    return f[0].replace(app.config['FLATPAGES_ROOT'] + '/', '')


def slugify(text, delim=u'-'):
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word)
        if word:
            result.append(word)
    return delim.join(result)
