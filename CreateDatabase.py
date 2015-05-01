#!/usr/bin/python

import sqlite3
conn = sqlite3.connect('picture_share.db')

c = conn.cursor()

# Turn on foreign key support
c.execute("PRAGMA foreign_keys = ON")

# Create users table
c.execute('''CREATE TABLE users
	     (email TEXT NOT NULL, 
	      password TEXT NOT NULL,
	      PRIMARY KEY(email))''')

# Friends
c.execute('''CREATE TABLE friends
	     (name TEXT NOT NULL,
         friend TEXT NOT NULL,
	      FOREIGN KEY (name) REFERENCES users(email),
	      FOREIGN KEY (friend) REFERENCES users(email),
	      PRIMARY KEY(name, friend))''')
          
# Friend Requests
c.execute('''CREATE TABLE friendRequests
	     (name TEXT NOT NULL,
         friend TEXT NOT NULL,
	      FOREIGN KEY (name) REFERENCES users(email),
	      FOREIGN KEY (friend) REFERENCES users(email),
	      PRIMARY KEY(name, friend))''')
          
# Posting
c.execute('''CREATE TABLE posts
	     (owner TEXT NOT NULL,
         circles TEXT NOT NULL,
         picture TEXT,
         details TEXT NOT NULL,
	      FOREIGN KEY (owner) REFERENCES users(email),
          FOREIGN KEY (circles) REFERENCES circleOfCircles(name),
          FOREIGN KEY (picture) REFERENCES pictures(path),
	      PRIMARY KEY(owner, circles, picture, details))''')

#Circle of circle
c.execute('''CREATE TABLE circleOfCircles
	     (ID TEXT NOT NULL,
         circleName TEXT NOT NULL,
          FOREIGN KEY (circleName) REFERENCES circles(name),
	      PRIMARY KEY(ID, circleName))''')

# Circle
c.execute('''CREATE TABLE circles
	     (name TEXT NOT NULL,
         friend TEXT NOT NULL,
         owner TEXT NOT NULL,
 	      FOREIGN KEY (friend) REFERENCES users(email),
          FOREIGN KEY (owner) REFERENCES users(email),
	      PRIMARY KEY(name, friend, owner))''')

# Create pictures table
c.execute('''CREATE TABLE pictures
	     (path TEXT,
	      album TEXT NOT NULL,
	      owner TEXT NOT NULL,
	      FOREIGN KEY(album, owner) REFERENCES albums(name, owner),
	      FOREIGN KEY(owner) REFERENCES users(email),
	      PRIMARY KEY(path))''')

# Create sessions table
c.execute('''CREATE TABLE sessions
	     (user TEXT NOT NULL,
	      session TEXT NOT NULL,
	      FOREIGN KEY(user) REFERENCES users(email),
	      PRIMARY KEY(session))''')


# Save the changes
conn.commit()

# Close the connection
conn.close()


# Create album table
# Visibility is 'public' or 'private'
# c.execute('''CREATE TABLE albums
#          (name TEXT NOT NULL,
#           owner TEXT NOT NULL,
#           visibility TEXT NOT NULL,
#           FOREIGN KEY (owner) REFERENCES users(email),
#           PRIMARY KEY(name, owner))''')
