date: 2016-10-29 23:07:04.784839
tags: ''
title: Static Site and Blog with Frozen-Flask

This site's been running on a Django backend for 3 years now. Looking back at 
my first post (which is like 4 posts down from this one... it hasn't been a 
particularly productive 3 years), I was excited about switching over to python
for development but a little apprehensive about working with a new framework.
Since then, I've gone through phases of different stack combinations
and I've settled on Flask as a RESTful API as my goto backend, coupled with 
either a fancy React frontend or something a little simpler with Flask and 
jQuery. I've learned quite a bit about setting up quick and maintainable 
web applications.

With all this elaborate technology available, another thing I hope I've learned
is restraint. The content on this site rarely changes, and certainly not in a way
that necessitates an always-on WSGI app backed up with a relational database.
There are several pre-built static site and blog generators out there, with
[Jekyll](https://jekyllrb.com/) probably being the most popular. I enjoy
working with Flask, so I decided to roll my own based on Flask-FlatPages, which
generates pages based on markdown files, and Frozen-Flask, which "freezes" a
Flask app so that it can be served as static files.

After deciding on a directory structure, the only thing to do was to write
URL generators so that Frozen-Flask could find my blog posts. I added in a few
scripts to generate page and posts templates, then duplicated the "old" layout
using [Skeleton](http://getskeleton.com/). Though I've still got work to do
with respect to bringing this site up to date, I'm definitely happy with the
changeover to a static distribution.

Another advantage of moving this site to Flask-FlatPages is that all the posts
and pages can be kept under version control. This entire site, including the
Flask scripts, are 
[available on github](https://github.com/bmbove/flask-static-homepage).
