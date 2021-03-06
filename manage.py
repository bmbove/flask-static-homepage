#! /usr/bin/env python
from datetime import datetime
import glob
import os
import yaml
import shutil
import sys
from subprocess import call

from flask import current_app
from flask_script import Manager, Server
from app import create_app, freezer

from utils import makeslug 

manager = Manager(create_app)
manager.add_command('runserver', Server(host='0.0.0.0', port='8000'))

@manager.command
def build():
    freezer.freeze()

@manager.command
def deploy():
    try:
        build()
        call(current_app.config['DEPLOY_CMD'], shell=True)
    except Exception as e:
        print(e)

@manager.option('-t', '--title', dest='title', default=None)
def createpage(title):

    if title is None:
        title = input("Page title: ")
    if title.strip() == '':
        exit("Page title cannot be blank")

    # generate path based on slug and date
    slug = makeslug(title) 
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
    slug = makeslug(title) 
    #datestring = datetime.now().strftime('%Y-%m-%d')
    now = datetime.now()
    base_path = os.path.join(
        'content',
        'posts',
        str(now.year),
        "%s-%s-%s" % (str(now.month).zfill(2), str(now.day).zfill(2), slug)
    );
    pathname = base_path
    filename = slug
    # check for duplicates, add a number to the end if there are any
    i = 0
    while(len(glob.glob(pathname)) != 0):
        i += 1
        pathname = '%s-%d' % (base_path, i)
        filename = '%s-%d' % (slug, i)

    # create tree
    os.makedirs(pathname)
    os.mkdir(os.path.join(pathname, 'assets'))

    # create post markdown file, write a default header
    with open(os.path.join(pathname, '%s.md' % filename), 'w') as fh:
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

    print('Created post %s in %s' % (title, pathname))


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
