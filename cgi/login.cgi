#!/usr/bin/python

# Import the CGI, string, sys modules
import cgi, string, sys, os, re, random
import cgitb; cgitb.enable()  # for troubleshooting
import sqlite3
import session
import base64
import Cookie
import smtplib

#Get Databasedir
MYLOGIN="rahluwal"
DATABASE="/homes/"+MYLOGIN+"/MyLink/picture_share.db"
IMAGEPATH="/homes/"+MYLOGIN+"/MyLink/images"
STYLESHEET="/homes/"+MYLOGIN+"/MyLink/stylesheet.css"
ALL_ID_STRING="$$##ALL##$$"


##############################################################
# Define function to generate login HTML form.
def login_form():
    html="""
<HTML>
<HEAD>
<link rel="stylesheet" type="text/css" href="stylesheet.css">
<TITLE>Info Form</TITLE>
</HEAD>

<BODY id ="loginBody">

<center><H2 id="loginHeader">MyLink</H2></center>
    
<div id="loginBox">
<H3 id="loginText" >Login:</H3>

<TABLE BORDER = 0 id="loginTable">
<FORM METHOD=post ACTION="login.cgi">
<TR><TH>Username:</TH><TD><INPUT TYPE=text NAME="username"></TD><TR>
<TR><TH>Password:</TH><TD><INPUT TYPE=password NAME="password"></TD></TR>
</TABLE>
<INPUT TYPE=hidden NAME="action" VALUE="login">
<br />
<INPUT class="btn btn--gray-dark" TYPE=submit VALUE="Login">
</FORM>


<br />

<H3 id="signUpText">Sign Up:</H3>

<TABLE BORDER = 0 id="loginTable">
<FORM METHOD=post ACTION="login.cgi">
<TR><TH>Username:</TH><TD><INPUT TYPE=text NAME="username"></TD><TR>
<TR><TH>Password:</TH><TD><INPUT TYPE=password NAME="password"></TD></TR>
</TABLE>
<INPUT TYPE=hidden NAME="action" VALUE="signUp">
<br />
<INPUT class="btn btn--gray-dark" TYPE=submit VALUE="Sign Up">
</FORM>

</div>
</BODY>
</HTML>
"""
    print_html_content_type()
    print(html)


###################################################################
# Define function to test the password.
def check_password(user, passwd):

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    t = (user,)
    c.execute('SELECT * FROM users WHERE email=?', t)

    row = stored_password=c.fetchone()
    conn.close();

    if row != None: 
      stored_password=row[1]
      if (stored_password==passwd):
         return "passed"

    return "failed"

##########################################################
# Diplay the options of admin
def display_admin_options(user, session):
    html="""
        <HEAD>
        <link rel="stylesheet" type="text/css" href="stylesheet.css">
        <TITLE>Info Form</TITLE>
        </HEAD>
        
        <H1 id="homepageHeader"> MyLink </H1>
        <div id="sidebar">
        <ul>
        <li> <a href="login.cgi?action=upload&user={user}&session={session}">Upload Picture</a>
        <li> <a href="login.cgi?action=show_image&user={user}&session={session}">Show Image</a>
        <li> <a href="login.cgi?action=changePassword&user={user}&session={session}">Change Password</a>
        <li> <a href="login.cgi?action=addFriend&user={user}&session={session}">Add Friend</a>
        <li> <a href="login.cgi?action=seeFriendRequests&user={user}&session={session}">See Friend Requests</a>
        <li> <a href="login.cgi?action=friendList&user={user}&session={session}">Friend List</a>
        <li> <a href="login.cgi?action=createCircleOfFriends&user={user}&session={session}">Create Circle Of Friends</a>
        <li> <a href="login.cgi?action=seeCircleOfFriends&user={user}&session={session}">See Circle Of Friends</a>
        <li> <a href="login.cgi?action=createPost&user={user}&session={session}">Create A Post</a>
        <li> <a href="login.cgi?action=validateAccount&user={user}&session={session}">Validate Account</a>
        
        
        <li> <a href="login.cgi?action=logout&user={user}&session={session}">Logout</a>
        </ul>
        </div>
        """
        #Also set a session number in a hidden field so the
        #cgi can check that the user has been authenticated
    html = html.format(user=user,session=session)
    print_html_content_type()
    print(html)
    showNewsFeed(user, session)

#################################################################
def create_new_session(user):
    return session.create_session(user)

##############################################################
def new_album(form):
    #Check session
    if session.check_session(form) != "passed":
       return

    html="""
        <H1> New Album</H1>
        """
    print_html_content_type()
    print(html);

##############################################################
def show_image(form):
    #Check session
    if session.check_session(form) != "passed":
       login_form()
       return

    # Your code should get the user album and picture and verify that the image belongs to this
    # user and this album before loading it

    #username=form["username"].value
    user = form["user"].value
    path = IMAGEPATH + "/"+user+"/profile.jpg";
    
    if not os.path.exists(path):
        display_admin_options(user, form["session"].value)
        return;
        
    # Read image
    with open(path, 'rb') as content_file:
       content = content_file.read()

    # Send header and image content
    hdr = "Content-Type: image/jpeg\nContent-Length: %d\n\n" % len(content)
    print hdr+content

###############################################################################

def upload(form):
    if session.check_session(form) != "passed":
       login_form()
       return

    html="""
        <HTML>
        <HEAD>
        <link rel="stylesheet" type="text/css" href="stylesheet.css">
        <TITLE>Info Form</TITLE>
        </HEAD>
        <FORM ACTION="login.cgi" METHOD="POST" enctype="multipart/form-data">
            <input type="hidden" name="user" value="{user}">
            <input type="hidden" name="session" value="{session}">
            <input type="hidden" name="action" value="upload-pic-data">
            <BR><I>Browse Picture:</I> <INPUT TYPE="FILE" NAME="file">
            <br>
            <input type="submit" value="Press"> to upload the picture!
            </form>
        </HTML>
    """

    user=form["user"].value
    s=form["session"].value
    print_html_content_type()
    print(html.format(user=user,session=s))

#######################################################

def upload_pic_data(form):
    #Check session is correct
    if (session.check_session(form) != "passed"):
        login_form()
        return

    #Get file info
    fileInfo = form['file']

    #Get user
    user=form["user"].value
    s=form["session"].value

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Check if the file was uploaded
    if fileInfo.filename:
        
        if not os.path.exists(IMAGEPATH+'/'+user):
            os.makedirs(IMAGEPATH+'/'+user)
            
        # Remove directory path to extract name only
        fileName = os.path.basename(fileInfo.filename)
        open(IMAGEPATH+'/'+user+'/profile.jpg', 'wb+').write(fileInfo.file.read())
            
        image_url="login.cgi?action=show_image&user={user}&session={session}".format(user=user,session=s)
        print_html_content_type()
	print ('<H2>The picture ' + fileName + ' was uploaded successfully</H2>')
        print('<image src="'+image_url+'">')
        picture=('/'+user+'/profile.jpg', '$PROFILE', user);
        t= ("$PROFILE", )
        c.execute("DELETE from pictures where album=?",t)
        c.execute('INSERT INTO pictures VALUES (?,?,?)', picture)
        conn.commit()

    else:
        message = 'No file was uploaded'

def print_html_content_type():
	# Required header that tells the browser how to render the HTML.
	print("Content-Type: text/html\n\n")
    
def createNewUser(form):
    username=form["username"].value
    password=form["password"].value
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    t = (username,)
    c.execute('SELECT * FROM users WHERE email=?', t)
    p = c.fetchone()
    if p:
        #means we have an existing user
        login_form();
        print("<H3 id=\"message\"><font color=\"red\">Someone exists with that email address.</font></H3>")
    else:
        #We can create user
        user=(username, password)
        c.execute('INSERT INTO users VALUES (?,?)', user)
        conn.commit()
        login_form();
        print("<H3 id=\"message\"><font color=\"green\">Your account has been created!</font></H3>")
        
def changePassword(form):
    #Check session is correct
    if (session.check_session(form) != "passed"):
        login_form()
        return
 
    
    html=""" 
        <HTML>
        <HEAD>
        <link rel="stylesheet" type="text/css" href="stylesheet.css">
        <TITLE>Info Form</TITLE>
        </HEAD>

        <BODY BGCOLOR = white>

        <center><H2 id="homepageHeader">Change Password</H2></center>


        <TABLE BORDER = 0 id="passwordTable">
        <tr>
        <td>
        <FORM METHOD=post NAME="passwordForm" ACTION="login.cgi">
        <TR><TH>Old Password:</TH><TD><INPUT TYPE=password NAME="oldPassword" ></TD><TR>
        <TR><TH>New Password:</TH><TD><INPUT TYPE=password NAME="newPassword"></TD></TR>
        <INPUT TYPE=hidden NAME="action" VALUE="actuallyChangePassword">
        <INPUT TYPE=hidden NAME="username" VALUE="{username}">
        </td>
        </tr>
        <tr>
        <td>
    <a href="#" class="btn btn--gray-dark" onclick="document.forms['passwordForm'].submit(); return false;" VALUE="Submit">Submit</a>
    </td>
    </tr>
    </TABLE>
    
    </FORM>
    </BODY>
    </HTML>
    """.format(username = form["user"].value)
    
    
    print_html_content_type();
    print(html)
    
def actuallyChangePassword(form):
    username=form["username"].value
    oldPassword = form["oldPassword"].value
    newPassword = form["newPassword"].value
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    t = (username, oldPassword,)
    j = (newPassword ,username, )
    c.execute('SELECT * FROM users WHERE email=? AND password=?', t)
    p = c.fetchone()
    if(p):
        #Correct old password
        c.execute("UPDATE users SET password=? WHERE email=?;",j)
        conn.commit()
        login_form();
        print("<H3 id=\"message\"><font color=\"green\">Password Changed!</font></H3>")
    else:
        login_form();
        print("<H3 id=\"message\"><font color=\"red\">Incorrect Details!</font></H3>")
        
def showAddFriendPage(form):
    #Check session is correct
    if (session.check_session(form) != "passed"):
        login_form()
        return
    ssn = form["session"].value

        
    print_html_content_type();
    html = """
    <HTML>
    <HEAD>
    <link rel="stylesheet" type="text/css" href="stylesheet.css">
    <TITLE>Info Form</TITLE>
    </HEAD>

    <BODY BGCOLOR = white>

    <center><H2>MyLink Add Friend</H2></center>

    <H3>Search For Friend:</H3>

    <TABLE BORDER = 0>
    <FORM METHOD=post ACTION="login.cgi">
    <TR><TH>Email:</TH><TD><INPUT TYPE=text NAME="email"></TD><TR>
    </TABLE>
    <INPUT TYPE=hidden NAME="action" VALUE="searchForFriend">
    <INPUT TYPE=hidden NAME="username" VALUE="{username}">
    <INPUT TYPE=hidden NAME="session" VALUE="{session}">
    <INPUT TYPE=submit VALUE="Enter">
    </FORM>
    </BODY>
    </HTML>"""
    print(html.format(username = form["user"].value, session=ssn));
    
def printFriendLink(ssn, user, friend):
    html = """
    <li><a href="login.cgi?action=actuallyAddFriend&user={user}&friend={name}&session={session}">{name}</a></li>
    """
    print(html.format(user=user, name=friend,session=ssn))
     
def searchForFriend(form):
    user = form["username"].value
    friend = form["email"].value
    ssn = form["session"].value
    t = (friend ,)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email LIKE ?', t)
    
    a = c.fetchall();
    
    html = """<HEAD>
<link rel="stylesheet" type="text/css" href="stylesheet.css">
<TITLE>Info Form</TITLE>
</HEAD>
<H1> Search Results </H1>
    <ul>"""
    
    print_html_content_type();
    print(html);
    for something in a:
        printFriendLink(ssn,user,something[0]);

    
    print("""
        </ul>
    """);

def actuallyAddFriend(form):
    user = form["user"].value
    friend = form["friend"].value
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    friendsOne = (user, friend, )
    c.execute('SELECT * from friends where name=? AND friend=?',friendsOne)
    a = c.fetchone()
    if a:
        display_admin_options(user, form["session"].value)
        message = "<H3 id=\"message\"><font color=\"red\">{you} and {friend} are already friends!</font></H3>"
        print(message.format(you=user, friend=friend));
        return

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    t = (friend ,)
    #set an entry in table so that main key is the friends email
    #that way, when we search for existing friend requests, we just search the primary key
    request=(friend, user)
    c.execute('INSERT INTO friendRequests VALUES (?,?)', request)
    conn.commit();
    session=create_new_session(user)
    display_admin_options(user, session)
    print("<H3 id=\"message\"><font color=\"green\">Friend Request Sent!</font></H3>")


def printFriendRequestLink(ssn, user, friend):
    html = """
    <li>{name}: &nbsp;<a href="login.cgi?action=confirmFriendRequest&user={user}&friend={name}&session={session}"> Accept,</a>&nbsp; 
    <a href="login.cgi?action=declineFriendRequest&user={user}&friend={name}&session={session}"> Decline</a>
     </li>
    """
    print(html.format(user=user, name=friend,session=ssn))



def showFriendRequests(form):

    #Check session is correct
    if (session.check_session(form) != "passed"):
        login_form()
        return

    user = form["user"].value
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    t = (user ,)
    c.execute('SELECT * FROM friendRequests WHERE name=?', t)

    a = c.fetchall();

    html = """<H1> Search Results </H1>
    <ul>"""
    
    print_html_content_type();
    print(html);
    ssn = form["session"].value;
    for something in a:
        printFriendRequestLink(ssn,user,something[1]);
    
    print("""
        </ul>
    """);


def declineFriendRequest(form):
    user = form["user"].value
    friend = form["friend"].value
    k = (user, friend, )
    c.execute('DELETE from friendRequests where name=? AND friend=?',k)
    conn.commit();
    display_admin_options(user, form["session"].value)
    message = "<H3 id=\"message\"><font color=\"red\">Friend request from {friend} declined!</font></H3>"
    print(message.format(friend=friend));

def confirmFriendRequest(form):
    user = form["user"].value
    friend = form["friend"].value

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    friendsOne=(user, friend,)
    friendsTwo=(friend,user,)
    c.execute('SELECT * from friends where name=? AND friend=?',friendsOne)
    a = c.fetchone()
    if a :
        display_admin_options(user, form["session"].value)
        message = "<H3 id=\"message\"><font color=\"red\">{you} and {friend} are already friends!</font></H3>"
        print(message.format(you=user, friend=friend));
        k = (user, friend, )
        c.execute('DELETE from friendRequests where name=? AND friend=?',k)
        conn.commit();
        return

    c.execute('INSERT INTO friends VALUES (?,?)', friendsOne)
    c.execute('INSERT INTO friends VALUES (?,?)', friendsTwo)
    k = (user, friend, )
    c.execute('DELETE from friendRequests where name=? AND friend=?',k)
    conn.commit();
    display_admin_options(user, form["session"].value)
    message = "<H3 id=\"message\"><font color=\"green\">{you} and {friend} are now friends!</font></H3>"
    print(message.format(you=user, friend=friend));

def printFriend(ssn, user, friend):
    html = """
    <li><a href="login.cgi?action=seeFriend&user={user}&friend={name}&session={session}">{name}</a></li>
    """
    # html = """
#     <li>{name}</li>"""
    print(html.format(user=user, name=friend,session=ssn))

def showFriendList(form):

    #Check session is correct
    if (session.check_session(form) != "passed"):
        login_form()
        return

    user = form["user"].value
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    t = (user ,)
    c.execute('SELECT * FROM friends WHERE name=?', t)

    a = c.fetchall();

    html = """
    <HEAD>
    <link rel="stylesheet" type="text/css" href="stylesheet.css">
    <TITLE>Info Form</TITLE>
    </HEAD>
    <H1> Friends </H1>
    <ul>"""
    
    print_html_content_type();
    print(html);
    ssn = form["session"].value;
    for something in a:
        printFriend(ssn,user,something[1]);
    
    print("""
        </ul>
    """);

def printFriendPage(picture, user, friend, ssn):
    print_html_content_type();
    hidden = "block"
    if picture != None:
        with open(IMAGEPATH+picture, 'rb') as content_file:
            pictureContent = base64.b64encode(content_file.read())
    else:
        pictureContent = "Bla"
        hidden = "none"
    html = """
    <HTML>
    <HEAD>
    <link rel="stylesheet" type="text/css" href="stylesheet.css">
    <TITLE>Info Form</TITLE>
    </HEAD>
    <BODY>
    <div id="profileBox">
    <img id="profileImage" src="data:image/png;base64,{picture}" alt="Profile Picture" style="display:{hidden};">
    <H3>{name}</H3>
    <a class="btn btn--gray-dark" href="login.cgi?action=removeFriend&user={user}&friend={name}&session={session}">Unfriend</a>
    </div>
    </BODY>
    </HTML> 
    """;
    print(html.format(picture=pictureContent, name=friend, hidden = hidden, user=user, session=ssn));

def showFriend(form):
    #Check session is correct
    if (session.check_session(form) != "passed"):
        login_form()
        return

    user = form["user"].value
    friend = form["friend"].value
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    t = (user ,friend, )
    c.execute('SELECT * FROM friends WHERE name=? AND friend=?', t)

    a = c.fetchone();

    if a==None:
        display_admin_options(user, form["session"].value)
        message = "<H3 id=\"message\"><font color=\"red\">{you} and {friend} are not friends!</font></H3>"
        print(message.format(you=user, friend=friend));
        return

    k = (friend, "$PROFILE", )
    c.execute('SELECT * FROM pictures WHERE owner=? AND album=?',k);
    a = c.fetchone();

    if a==None:
        printFriendPage(None, user, friend, form["session"].value)
    else:
        printFriendPage(a[0], user, friend, form["session"].value)

def removeFriend(form):    
    user = form["user"].value
    friend = form["friend"].value
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    t=(user, friend, )
    c.execute("DELETE FROM friends WHERE name=? AND friend=?", t)
    
    t=(friend, user, )
    c.execute("DELETE FROM friends WHERE name=? AND friend=?", t)
    conn.commit()
    
    display_admin_options(user, form["session"].value)
    
    message = "<H3 id=\"message\"><font color=\"green\">{you} and {friend} are no longer friends!</font></H3>"
    print(message.format(friend=friend, you = user));
    
def createFriendCheckbox(friendName):
    html = """<input type="checkbox" value={friend} name="friendName"/> {friend} <br />"""
    return html.format(friend=friendName);

def showCreateCircleOfFriends(form):
    #Check session is correct
    if (session.check_session(form) != "passed"):
        login_form()
        return
    
    user = form["user"].value
        
    html = """    
    <HTML>
    <HEAD>
    <link rel="stylesheet" type="text/css" href="stylesheet.css">
    <TITLE>Info Form</TITLE>
    </HEAD>
    <H3>Create Circle Of Friends:</H3>

    <TABLE BORDER = 0>
    <FORM METHOD=post ACTION="login.cgi">
    {friends}
    <TR><TH>Circle Name:</TH><TD><INPUT TYPE=text NAME="circleName"></TD><TR>
    </TABLE>
    <INPUT TYPE=hidden NAME="action" VALUE="actuallyCreateCircleOfFriends">
    <INPUT TYPE=hidden NAME="user" VALUE="{user}">
    <INPUT TYPE=hidden NAME="session" VALUE="{session}">
    <INPUT TYPE=submit VALUE="Enter">
    </FORM>
    </HTML>
    """
    
    friends = """ """;
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    t = (user, )
    c.execute('SELECT * FROM friends WHERE name=?', t)
    a = c.fetchall();
    
    for something in a:
        friends += createFriendCheckbox(something[1])
    s = form["session"].value
    html = html.format(friends=friends, user=user, session=s)
    print_html_content_type();
    print(html);
    
def actuallyCreateCircleOfFriends(form):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
   
    
    friends = form.getlist("friendName");
    circleName = form['circleName'].value;
    user = form['user'].value
    
    for friend in friends:
        if friend:
            #checked!
            t = (circleName, friend, user, )
            c.execute("INSERT INTO circles VALUES (?,?,?)",t);
            conn.commit();

    
    s = form["session"].value

    #print_html_content_type();
    display_admin_options(user, s)
    message = "<H3 id=\"message\"><font color=\"green\">{circle} created!</font></H3>"
    print(message.format(circle=circleName));
    
    
def reassignCircle(form):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    friends = form.getlist("friendName")
    circle=form["circle"].value
    user = form["user"].value
    t=(user, )
    
    
    t=(user, circle, )
    c.execute("DELETE from circles where owner=? AND name=?",t)
    
    for friend in friends:
        if friend:
            k=(circle, friend, user, )
            c.execute("INSERT into circles VALUES (?,?,?)",k)
    
    conn.commit()
    display_admin_options(user, form["session"].value)
    print(circle);
    
def showCircleOfFriends(form):
    #Check session is correct
    if (session.check_session(form) != "passed"):
        login_form()
        return
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    user = form["user"].value
    t = (user, )
    c.execute("SELECT * FROM circles where owner=?",t);
    a = c.fetchall();
    done = []
    html = """ """
    for something in a:
        try:
            index = done.index(something[0])
        except ValueError:
            index = -1
            
        if index != -1:
            continue;
    
        k = """<li> <a href="login.cgi?action=editCircle&circle={circle}&user={user}&session={session}">{circle}</a>"""
        done.append(something[0]);
        html += k.format(user=user,session=form["session"].value,circle=something[0]);
        
    mainHtml="""<HTML>
    <HEAD>
    <link rel="stylesheet" type="text/css" href="stylesheet.css">
    <TITLE>Info Form</TITLE>
    </HEAD>
    <H3>Circle Of Friends</H3>

    <TABLE BORDER = 0>
    {circles}
    </TABLE>
    </HTML>"""
    
    print_html_content_type();
    print(mainHtml.format(circles=html));
    
    
def showEditCirclePage(form):
    #Check session is correct
    if (session.check_session(form) != "passed"):
        login_form()
        return
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    user = form["user"].value
    circle = form["circle"].value
    s = form["session"].value
    
    t = (user, circle, )
    c.execute("SELECT * FROM circles where owner=? AND name=?",t);
    circles = c.fetchall()
    
    t = (user, )
    c.execute("SELECT * FROM friends where name=?",t);
    
    a = c.fetchall()
    
    html = """ """
    
    for row in a:
        checked = ""
        
        for circle in circles:
            if circle[1] == row[1]:
                checked = "checked"
                
        k = """<li><input type="checkbox" value="{friend}" name="friendName" {checked}> {friend} </input></li>"""
        html += k.format(friend=row[1], checked=checked);
    
    
    mainHtml="""
        <HTML>
        <HEAD>
        <link rel="stylesheet" type="text/css" href="stylesheet.css">
        <TITLE>Info Form</TITLE>
        </HEAD>
        <H3>Edit Circle:</H3>
        <FORM ACTION="login.cgi" id="postForm" METHOD="POST" enctype="multipart/form-data">
            <input type="hidden" name="user" value="{user}">
            <input type="hidden" name="session" value="{session}">
            <input type="hidden" name="circle" value="{circle}">
            <input type="hidden" name="action" value="reassignCircle">
            <ul>
            {friends}
            </ul>
            <input type="submit" value="Submit">
            </form>
        </HTML>
    """
    print_html_content_type()
    print(mainHtml.format(friends=html,user=user,session=s,circle=circle));
        
def getCircleNames(user):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    t = (user, )
    c.execute("SELECT * FROM circles where owner=?",t);
    a = c.fetchall();
    done = []
    html = """ """
    for something in a:
        
        try:
            index = done.index(something[0])
        except ValueError:
            index = -1
            
        if index != -1:
            continue;
            
        k = """<input type="checkbox" value="%s" name="circleName">%s</option><br />""" % (something[0], something[0])
        
        done.append(something[0]);
        html += k
    
    return html;

def showCreatePost(form):
    #Check session is correct
    if (session.check_session(form) != "passed"):
        login_form()
        return
        
    html="""
        <HTML>
        <HEAD>
        <link rel="stylesheet" type="text/css" href="stylesheet.css">
        <TITLE>Info Form</TITLE>
        </HEAD>
        <H2 id="homepageHeader">Create A Post</H2>
        <div id="postDiv">
        <FORM ACTION="login.cgi" id="postForm" METHOD="POST" enctype="multipart/form-data">
            <input type="hidden" name="user" value="{user}">
            <input type="hidden" name="session" value="{session}">
            <input type="hidden" name="action" value="upload-post">
            <textarea name="post" form="postForm" rows="4" cols="50" placeholder="Share your thoughts..."></textarea>
            <br />
            <br />
            <TABLE>
            {circles}
            </TABLE>
            <br />
            <BR><I>Browse Picture:</I> <INPUT TYPE="FILE" NAME="file">
            <br>
            <br />
            <input type="submit" value="Submit">
            </form>
        </div>
        </HTML>
    """
    user = form["user"].value
    circleNames = getCircleNames(user)
    html = html.format(user=user, session=form["session"].value, circles=circleNames)
    print_html_content_type();
    print(html);
    
def uploadPost(form):
    #Check session is correct
    if (session.check_session(form) != "passed"):
        login_form()
        return
        
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    #Get file info
    fileInfo = form['file']

    #Get user
    user=form["user"].value
    s=form["session"].value
    postDetails = form["post"].value

    circleNames = form.getlist("circleName");
    
    n=20
    char_set = string.ascii_uppercase + string.digits
    ID = ''.join(random.sample(char_set,n))
        
    checkedOne = "no"
    for circleName in circleNames:
        if circleName:
            checkedOne = "yes"
            t = (circleName, )
            c.execute("SELECT * FROM circleOfCircles WHERE circleName=?",t)
            k = c.fetchone();
            if k:
                ID = k[0];
            else:
                t = (ID, circleName)
                c.execute("INSERT INTO circleOfCircles VALUES (?,?)", t)
                
    
    
    if fileInfo.filename:
        #IMAGE WAS POSTED
        # Remove directory path to extract name only
        fileName = os.path.basename(fileInfo.filename)
        path = "/%s/%s" % (user,fileName)
        path2 = "/%s" % user
        if not os.path.exists(IMAGEPATH+path2):
            os.makedirs(IMAGEPATH+path2)

        open(IMAGEPATH+path, 'wb').write(fileInfo.file.read())

        #image_url="login.cgi?action=show_image&user={user}&session={session}".format(user=user,session=s)
        #print('<image src="'+image_url+'">')
        
    else:
        path = None



    if checkedOne == "no":
        ID = ALL_ID_STRING
    post=(user, ID, path, postDetails);
    c.execute('INSERT INTO posts VALUES (?,?,?,?)', post)
    conn.commit()

    #print_html_content_type()
    display_admin_options(user, s)
    message = "<H3 id=\"message\"><font color=\"green\">Your post was posted!</font></H3>"
    print(message);
    
def belongsToCircle(user ,circleName):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    t = (circleName[1], user, )
    c.execute('SELECT * FROM circles WHERE name=? AND friend=?',t)
    a = c.fetchone()
    
    if a:
        return "yes";
    
    return "no";
    
def showNewsFeed(user, s):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    

    q=(user, )
    c.execute('SELECT * FROM circles WHERE friend=?', q)
    a = c.fetchall();
    
    circles = []
    for row in a:
        circles.append(row[0]);
    
    c.execute('SELECT * FROM posts')
    a = c.fetchall();
    
    posts = []
    
    # for row in a:
 #        if belongsToCircle(row[1],circles) == "yes":
 #            posts.append(row);
 #        elif row[0] == user
 #            posts.append(row);
 
    for row in a:
        circleID = row[1]
        t= (circleID, )
        if row[0] == user:
            posts.append(row);
            continue;
        if row[1] == ALL_ID_STRING:
            posts.append(row);
            continue;
        c.execute('SELECT * from circleOfCircles WHERE ID=?', t)
        k = c.fetchall();
        for circle in k:
            if belongsToCircle(user, circle) == "yes":
                posts.append(row);
                
                
    # <HTML>
    # <HEAD>
    # <link rel="stylesheet" type="text/css" href="stylesheet.css">
    # <TITLE>Info Form</TITLE>
    # </HEAD>
    #
    # <BODY BGCOLOR = white>
    #
    # <center><H2>MyLink News Feed</H2></center>


        
    #Now we need to show these posts
    html = """
    
    <TABLE BORDER = 0 id="postsTable">
    {posts}
    </TABLE>
    </BODY>
    </HTML>"""
    
    postsHtml = """ """
    
    postBox = """
    <TR>
    <TD>
    <div id="postBox">
    <img id="postImage" src="data:image/png;base64,{picture}" alt="Post Picture" style="display:{hidden}">
    <p id="postText">
    {text}
    </p>
    <p style = "" id="postOwner">
    By {owner}
    </p>
    </div></TD></TR>"""
    for post in reversed(posts):
        owner = post[0];
        pictureContent = None;
        if post[2] == None:
            picture = None;
        else:
            picture = IMAGEPATH + post[2];
            with open(picture, 'rb') as f:
                pictureContent = base64.b64encode(f.read())
        details = post[3];
        hidden = "block";
        if picture == None:
            hidden = "none"
        postsHtml += postBox.format(picture=pictureContent, owner = owner, text = details, hidden = hidden);
    
    html = html.format(posts = postsHtml);
    # print_html_content_type()
    print(html);
    

def validateAccount(form):
    sender = 'myLink@myLink.com'
    receivers = [form["user"].value]

    message = """
    Please click the following link to validate your account.
    {link}
    Thank You,
    The MyLink Team.
    """
    
    link = """ http://data.cs.purdue.edu:1224/MyLink/login.cgi?user={user}&action=actuallyValidateAccount 
    """
    link = link.format(user=receivers[0])
    message = message.format(link=link)
    try:
        smtpObj = smtplib.SMTP("localhost")
        smtpObj.sendmail(sender, receivers, message)
        display_admin_options(receivers[0],form["session"].value);
        print("<H3 id=\"message\"><font color=\"green\">Sent Verification</font></H3>")
    except smtplib.SMTPException:
        display_admin_options(receivers[0],form["session"].value); 
        print("<H3 id=\"message\"><font color=\"red\">Unable To Send Verification</font></H3>")
    
    
##############################################################
# Define main function.
def main():
    form = cgi.FieldStorage()
    if "action" in form:
        action=form["action"].value
        #print("action=",action)
        if action == "login":
            #we need to check cookie
            try:
                cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
                user = cookie["user"].value
                session = cookie["session"].value
                display_admin_options(user, session)
                return;
            except (Cookie.CookieError, KeyError):
                if "username" in form and "password" in form:
                    #Test password
                    username=form["username"].value
                    password=form["password"].value
                    if check_password(username, password)=="passed":
                       session=create_new_session(username)
                       #no cookie, so set one
                       cookie = Cookie.SimpleCookie()
                       cookie["session"] = session
                       cookie["user"] = username
                       print cookie.output()
                       display_admin_options(username, session)
                    else:
                       login_form()
                       print("<H3 id=\"message\"><font color=\"red\">Incorrect user/password</font></H3>")
            
        elif (action == "signUp"):
            createNewUser(form);
        elif (action == "new-album"):
	        new_album(form)
        elif (action == "upload"):
            upload(form)
        elif (action == "show_image"):
            show_image(form)
        elif action == "upload-pic-data":
            upload_pic_data(form)
        elif action == "changePassword":
            changePassword(form);
        elif action == "actuallyChangePassword":
            actuallyChangePassword(form);
        elif action == "addFriend":
            showAddFriendPage(form);
        elif action == "searchForFriend":
            searchForFriend(form);
        elif action == "actuallyAddFriend":
            actuallyAddFriend(form);
        elif action == "seeFriendRequests":
            showFriendRequests(form);
        elif action == "confirmFriendRequest":
            confirmFriendRequest(form);
        elif action == "declineFriendRequest":
            declineFriendRequest(form);
        elif action == "friendList":
            showFriendList(form);
        elif action == "seeFriend":
            showFriend(form);
        elif action == "removeFriend":
            removeFriend(form);
        elif action == "createCircleOfFriends":
            showCreateCircleOfFriends(form);
        elif action == "seeCircleOfFriends":
            showCircleOfFriends(form);
        elif action == "editCircle":
            showEditCirclePage(form);
        elif action == "actuallyCreateCircleOfFriends":
            actuallyCreateCircleOfFriends(form);
        elif action == "createPost":
            showCreatePost(form);
        elif action == "upload-post":
            uploadPost(form);
        elif action == "showNewsFeed":
            user = form["user"].value
            s = form["session.value"];
            showNewsFeed(user, s);
        elif action == "validateAccount":
            validateAccount(form);
        elif action == "reassignCircle":
            reassignCircle(form);
        elif action == "actuallyValidateAccount":
            login_form();
            print("<H3 id=\"message\"><font color=\"green\">Thank You For Your Verification.</font></H3>")
        elif action == "logout":
            c=Cookie.SimpleCookie()
            c['session']=''
            c['user']=''
            c['session']['expires']='Thu, 01 Jan 1970 00:00:00 GMT'
            c['user']['expires']='Thu, 01 Jan 1970 00:00:00 GMT'
            print c.output()
            login_form();
        else:
            login_form()
    else:
        #we need to check cookie
        try:
            cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
            user = cookie["user"].value
            session = cookie["session"].value
            display_admin_options(user, session)
            return;
        except (Cookie.CookieError, KeyError):
            login_form()

###############################################################
# Call main function.
main()
