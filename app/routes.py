from app import app, db
from app.models import Restaurant, MenuItem
from app.google_auth_config import google_secrets_config, AUTHORIZATION_SCOPE
from app.utils import credentials_to_dict

import flask
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask import session as login_session

import random, string

import google.oauth2.credentials
import google_auth_oauthlib.flow


# Show all restaurants
@app.route('/')
@app.route('/index')
@app.route('/home')
@app.route('/restaurant/')
def showRestaurants():
  restaurants = Restaurant.query.order_by(Restaurant.name.asc())
  return render_template('restaurants.html', restaurants = restaurants)

# Create anti-forgery token
# @app.route('/login')
# def showLogin():
#     # state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
#     # login_session['state'] = state
#     #return "The current session state is %s" % login_session['state'] 
#     return render_template('auth.html')


@app.route('/login')
def authorize():
    # https://developers.google.com/identity/protocols/oauth2/web-server#example
    # https://www.mattbutton.com/2019/01/05/google-authentication-with-python-and-flask/
    # https://realpython.com/flask-google-login/
    
    # create a Flow instance to manage the 0Auth 2.0 Authorization Grant Flow steps
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        google_secrets_config,
        scopes=AUTHORIZATION_SCOPE
    )
    flow.redirect_uri = url_for('loginCallback', _external=True)

    # Enable 
    # - offline access so that you can refresh an access token 
    #   without re-prompting the user for permission
    # - incremental authorization
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return redirect(authorization_url)


@app.route('/login/callback')
def loginCallback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        google_secrets_config,
        scopes=AUTHORIZATION_SCOPE,
        state=state
    )
    flow.redirect_uri = url_for('loginCallback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('showRestaurants'))



# @app.route('/logout')

#JSON APIs to view Restaurant Information
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).one()
    items = MenuItem.query.filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = MenuItem.query.filter_by(id = menu_id).one()
    return jsonify(Menu_Item = Menu_Item.serialize)

@app.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = Restaurant.all()
    return jsonify(restaurants= [r.serialize for r in restaurants])


# Create a new restaurant
@app.route('/restaurant/new/', methods=['GET','POST'])
def newRestaurant():
  if request.method == 'POST':
      newRestaurant = Restaurant(name = request.form['name'])
      db.session.add(newRestaurant)
      flash('New Restaurant %s Successfully Created' % newRestaurant.name)
      db.session.commit()
      return redirect(url_for('showRestaurants'))
  else:
      return render_template('newRestaurant.html')

#Edit a restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
  editedRestaurant = Restaurant.query.filter_by(id = restaurant_id).one()
  if request.method == 'POST':
      if request.form['name']:
        editedRestaurant.name = request.form['name']
        flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
        return redirect(url_for('showRestaurants'))
  else:
    return render_template('editRestaurant.html', restaurant = editedRestaurant)


#Delete a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
  restaurantToDelete = Restaurant.query.filter_by(id = restaurant_id).one()
  if request.method == 'POST':
    db.session.delete(restaurantToDelete)
    flash('%s Successfully Deleted' % restaurantToDelete.name)
    db.session.commit()
    return redirect(url_for('showRestaurants', restaurant_id = restaurant_id))
  else:
    return render_template('deleteRestaurant.html',restaurant = restaurantToDelete)

#Show a restaurant menu
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).one()
    items = MenuItem.query.filter_by(restaurant_id = restaurant_id).all()
    return render_template('menu.html', items = items, restaurant = restaurant)
     


#Create a new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new/',methods=['GET','POST'])
def newMenuItem(restaurant_id):
  restaurant = Restaurant.query.filter_by(id = restaurant_id).one()
  if request.method == 'POST':
      newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], restaurant_id = restaurant_id)
      db.session.add(newItem)
      db.session.commit()
      flash('New Menu %s Item Successfully Created' % (newItem.name))
      return redirect(url_for('showMenu', restaurant_id = restaurant_id))
  else:
      return render_template('newmenuitem.html', restaurant_id = restaurant_id)

#Edit a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):

    editedItem = MenuItem.query.filter_by(id = menu_id).one()
    restaurant = Restaurant.query.filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        db.session.add(editedItem)
        db.session.commit() 
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = editedItem)


#Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id,menu_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).one()
    itemToDelete = MenuItem.query.filter_by(id = menu_id).one() 
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item = itemToDelete)

    