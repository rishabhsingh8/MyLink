#!/usr/bin/python

import sqlite3
conn = sqlite3.connect('picture_share.db')
c = conn.cursor()

print
print 'Print all posts'
for row in c.execute('SELECT * FROM posts'):
  print row
  
print 'Print all Circles'
for row in c.execute('SELECT * FROM circles'):
  print row

print 'Print all CirclesOfCircles'
for row in c.execute('SELECT * FROM circleOfCircles'):
  print row
 
print 'Print all friends'
for row in c.execute('SELECT * FROM friends'):
  print row
 
print 'Print all pictures'
for row in c.execute('SELECT * FROM pictures'):
  print row

print 'Print all users'
for row in c.execute('SELECT * FROM users'):
  print row

print
print "Print peter's password"
t = ('peter@gmail.com',)
c.execute('SELECT * FROM users WHERE email=?', t)
print c.fetchone()[1]

