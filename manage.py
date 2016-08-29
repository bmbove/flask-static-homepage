#! /usr/bin/env python
from datetime import datetime
import glob
import os
import yaml
import shutil
import sys

from flask_script import Manager, Server
from app import create_app, freezer

from utils import slugify

manager = Manager(create_app)
manager.add_command('runserver', Server(host='0.0.0.0', port='8000'))

@manager.command
def build():
    freezer.freeze()

@manager.command
def deploy():
    assert False, "Not implemented yet"


@manager.option('-t', '--title', dest='title', default=None)
def createpage(title):

    if title is None:
        title = input("Page title: ")
    if title.strip() == '':
        exit("Page title cannot be blank")

    # generate path based on slug and date
    slug = slugify(title) 
    filename = '%s' % slug
    # check for duplicates, add a number to the end if there are any
    i = 0
    while(len(glob.glob(os.path.join('content', '%s.md' % filename))) != 0):
        i += 1
        filename = '%s-%d' % (slug, i)

    # create page markdown file, write a default header
    with open(os.path.join('content', '%s.md' % filename), 'w') as fh:
        header = {
            'title': title,
            'date': datetime.now(),
        }
        yaml.dump(
            header,
            fh,
            default_flow_style=False
        )
        fh.write('\n\n')

    print('Created page %s in %s.md' % (title, filename))


@manager.option('-t', '--title', dest='title', default=None)
def createpost(title):

    if title is None:
        title = input("Post title: ")
    if title.strip() == '':
        exit("Post title cannot be blank")

    # generate path based on slug and date
    slug = slugify(title) 
    datestring = datetime.now().strftime('%Y-%m-%d')
    pathname = '%s-%s' % (datestring, slug)
    filename = slug
    # check for duplicates, add a number to the end if there are any
    i = 0
    while(len(glob.glob(os.path.join('content', 'posts', pathname))) != 0):
        i += 1
        pathname = '%s-%s-%d' % (datestring, slug, i)
        filename = '%s-%d' % (slug, i)

    # create tree
    path = os.path.join('content', 'posts', pathname)
    os.mkdir(path)
    os.mkdir(os.path.join(path, 'assets'))

    # create post markdown file, write a default header
    with open(os.path.join(path, '%s.md' % filename), 'w') as fh:
        header = {
            'title': title,
            'date': datetime.now(),
            'tags': ''
        }
        yaml.dump(
            header,
            fh,
            default_flow_style=False
        )
        fh.write('\n\n')

    print('Created post %s in %s' % (title, path))


@manager.command
def flush():
    print("**This will delete all posts and pages, leaving no backup**")
    cont = input("Continue? [y/N] ")
    if cont.upper() != 'Y':
        exit("Flush aborted")

    dirs = glob.glob(os.path.join('content', 'posts/*'))
    for d in dirs:
        shutil.rmtree(d)

    files = glob.glob(os.path.join('content', '*.md'))
    for f in files:
        os.remove(f)

    with open(os.path.join('content', 'home.md'), 'w') as fh:
        header = {
            'title': 'Home',
            'date': datetime.now(),
        }
        yaml.dump(
            header,
            fh,
            default_flow_style=False
        )
        fh.write('\n\n# Welcome')
    print("Project flushed")

   

if __name__ == '__main__':
    manager.run()
