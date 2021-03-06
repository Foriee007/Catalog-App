from flask import Flask, render_template, url_for, request, redirect
from flask import jsonify, flash
from flask import make_response
from flask import session as login_session
# Imports for CRUD operations on database
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Items
# Needed to handle callback method, state token
import random
import string
import datetime
import httplib2
import json
import requests
# Imports for OAuth 2  authentication mechanism
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Credentials for Google OAuth
google_login = '/var/www/FlaskApp/FlaskApp/client_secrets.json'
CLIENT_ID = json.loads(
    open(google_login, 'r').read())['web']['client_id']

app = Flask(__name__)

#######################################################
# Connect to the Database and create a database session
#######################################################
# Create session and connect to the database
engine = create_engine('postgresql://catalog:catalog123@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

################################################
# Login; OAuth routes and functions here
###############################################


def createUser(login_session):
    print login_session
    newUser = User(
                name=login_session['username'],
                email=login_session['email'],
                picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Method to do the login, for now only with support for Google Plus
@app.route('/login')
def showLogin():
    # Create a state token to prevent request forgery and store it in
    # the session for later validation.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, login=True)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token that  server sent to the client,
    # confirm the user is making the request
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain ne-time authorization code from the server
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(google_login, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code'), 401)  # noqa
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)  # noqa
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID doesn't match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps("Current user is already connected"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['provider'] = 'google'
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # If the name field isn't blank, set the user's name to that. Otherwise,
    # set the user's name to their email address.
    if data['name']:
        login_session['username'] = data['name']
    else:
        login_session['username'] = data['email']
    login_session['email'] = data['email']
    login_session['picture'] = data['picture']

    # See if user exists, if they don't, add her!
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Welcome login message
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" class="img-circle" style = "width: 300px; height: 300px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


############################################################################
# DISCONNECT - Revoke a current user's token and reset their login session.
############################################################################
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps("Current user is not connected"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET request to revoke current token.
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session
        response = make_response(
            json.dumps("Successfully disconnected."), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/catalog')

    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke the token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect - Revoke a user's token and resset their login session
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        del login_session['state']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in to begin with!")
        return redirect(url_for('showCatalog'))


#############################################
# Basic Routing here:
# Show categories and most recent items
############################################

@app.route('/')
@app.route('/catalog/')
def showCatalog():
    '''This is the homepage which will show all current categories along with
    the latest added items. After logging in, a user has the ability to add,
    update or delete item info.'''
    catalog = session.query(Category).order_by(asc(Category.name))
    items = session.query(Items).order_by(desc(Items.date)).limit(5)
    print login_session
    if 'username' not in login_session:
        return render_template(
            'publicshowcatalog.html',
            categories=catalog,
            items=items)
    else:
        user = getUserInfo(login_session['user_id'])
        return render_template(
            'showcatalog.html',
            categories=catalog,
            items=items,
            user=user)


# Show specific category items
@app.route('/catalog/<category_name>/')
@app.route('/catalog/<category_name>/items/')
def showCategoryItems(category_name):
    catalog = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category=category)\
                                .order_by(asc(Items.name))
    count = session.query(Items).filter_by(category=category).count()
    if 'username' not in login_session:
        return render_template(
            'publicshowquotes.html',
            category=category.name,
            categories=catalog,
            items=items,
            count=count)
    else:
        user = getUserInfo(login_session['user_id'])
        return render_template(
            'showquotes.html',
            category=category.name,
            categories=catalog,
            items=items,
            count=count,
            user=user)


# Add an Quote  to Latest authors
@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    if request.method == 'POST':
        newItem = Items(
            name=request.form['name'],
            description=request.form['description'],
            picture=request.form['picture'],
            category=session.query(Category).filter_by(name=request.form['category']).one(),  # noqa
            date=datetime.datetime.now(),
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('Item Successfully Added!')
        return redirect(url_for('showCatalog'))
    else:
        user = getUserInfo(login_session['user_id'])
        return render_template(
            'addquote_to_topics.html',
            categories=categories,
            user=user)


# Add an Quote to a select topics category
@app.route('/catalog/<category_name>/add', methods=['GET', 'POST'])
def addCategoryItem(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    categories = session.query(Category).all()
    user = getUserInfo(login_session['user_id'])
    if request.method == 'POST':
        newItem = Items(
            name=request.form['name'],
            description=request.form['description'],
            picture=request.form['picture'],
            category=session.query(Category).filter_by(name=request.form['category']).one(),  # noqa
            date=datetime.datetime.now(),
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('Category Item Successfully Added!')
        return redirect(url_for('showCategoryItems', category_name=category.name))  # noqa
    else:
        return render_template(
            'addquote.html',
            category=category,
            categories=categories,
            user=user)


# Show the specifics of an Quote phase + Author on Pucture frame
@app.route('/catalog/<category_name>/<item_name>/')
def showItem(category_name, item_name):
    itemuser = session.query(Items).filter_by(name=item_name).one()
    categories = session.query(Category).order_by(asc(Category.name))
    creator = getUserInfo(itemuser.user_id)
    if 'username' not in login_session:
        return render_template(
            'publicquotephaseframe.html',
            item=itemuser,
            category=category_name,
            categories=categories)
        user = getUserInfo(login_session['user_id'])
        if 'username' not in login_session or creator.id != login_session.get('user_id'):  # noqa
            return render_template(
                'publicquotephaseframe.html',
                item=itemuser,
                category=category_name,
                categories=categories)
    else:
        return render_template(
            'quotephaseframe.html',
            item=itemuser,
            category=category_name,
            categories=categories,
            user=creator,
            creator=creator)


# Edit an Quote items
@app.route('/catalog/<category_name>/<item_name>/edit', methods=['GET', 'POST'])  # noqa
def editItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Items).filter_by(name=item_name).one()
    categories = session.query(Category).all()
    # Check if this user is the owner of the item before proceeding
    creator = getUserInfo(editedItem.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        return render_template(
            'publicquotephaseframe.html',
            item=editedItem,
            category=category_name,
            categories=categories,
            user=user)
    # POST methods
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['picture']:
            editedItem.picture = request.form['picture']
        if request.form['category']:
            category = session.query(Category).filter_by(name=request.form['category']).one()  # noqa
            editedItem.category = category
        time = datetime.datetime.now()
        editedItem.date = time
        session.add(editedItem)
        session.commit()
        flash('Category Item Successfully Edited!')
        return redirect(url_for(
            'showCategoryItems',
            category_name=editedItem.category.name,
            user=user))
    else:
        return render_template(
            'editquote.html',
            item=editedItem,
            categories=categories,
            user=user)


#########################
# Delete an Quote  items
########################
@app.route('/catalog/<category_name>/<item_name>/delete', methods=['GET', 'POST'])  # noqa
def deleteItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Items).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(name=category_name).one()
    categories = session.query(Category).all()
    # Check if this user is the owner of the item before proceeding
    creator = getUserInfo(itemToDelete.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        return render_template(
            'publicquotephaseframe.html',
            item=itemToDelete,
            category=category_name,
            categories=categories,
            user=user)
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted! We will miss that '+itemToDelete.name)
        return redirect(url_for(
            'showCategoryItems',
            category_name=category.name,
            user=user))
    else:
        return render_template(
            'deletequote.html',
            item=itemToDelete,
            user=user)


##################################################
# JSON APIs to view category and Item information
##################################################

@app.route('/catalog.json')
@app.route('/catalog.JSON')
def allItemsJSON():
    categories = session.query(Category).all()
    category_dict = [c.serialize for c in categories]
    # Best way I found to replicate the JSON call picture in the assignment
    # notes. Does this look ok?
    for c in range(len(category_dict)):
        items = [i.serialize for i in session.query(Items).filter_by(category_id=category_dict[c]["id"]).all()]  # noqa
        if items:
            category_dict[c]["Item"] = items
    return jsonify(Category=category_dict)


@app.route('/catalog/categories/json')
@app.route('/catalog/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/catalog/<category_name>/json')
@app.route('/catalog/<category_name>/JSON')
def categoryItemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category=category).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/catalog/<category_name>/<item_name>/json')
@app.route('/catalog/<category_name>/<item_name>/JSON')
def ItemJSON(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(
        name=item_name,
        category=category).one()
    return jsonify(item=[item.serialize])


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = 'localhost', port = 5000)
