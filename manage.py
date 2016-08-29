#! /usr/bin/env python
from datetime import datetime
import glob
import os
import yaml
import sys

from flask_script import Manager, Server
from app import create_app, freezer

from utils import slugify

manager = Manager(create_app)
manager.add_command('runserver', Server(host='0.0.0.0', port='5000'))

@manager.command
def build():
    freezer.freeze()

@manager.command
def deploy():
    assert False, "Not implemented yet"


@manager.option('-t', '--title', dest='title', default=None)
def createpost(title):
    if title is None:
        title = input("Post title: ")
    if title.strip() == '':
        exit("Post title cannot be blank")

    slug = slugify(title) 
    t = datetime.now()
    filename = "%d-%d-%d-%s" % (
        t.year,
        t.month,
        t.day,
        slug 
    )
    i = 1
    while(len(glob.glob(os.path.join('content', 'posts', filename))) != 0):
        filename = "%d-%d-%d-%s-%d" % (
            t.year,
            t.month,
            t.day,
            slug,
            i
        )
        i += 1
    path = os.path.join('content', 'posts', filename)
    os.mkdir(path)
    os.mkdir(os.path.join(path, 'assets'))

    with open(os.path.join(path, '%s.md' % slug), 'w') as fh:
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
   

if __name__ == '__main__':
    manager.run()
