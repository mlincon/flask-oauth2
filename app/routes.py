import os
import jwt
import json
import hashlib

import flask
from flask import Flask, request, jsonify, flash, session, redirect, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from app import app, db
from app.models import Restaurant, MenuItem
from app.utils import login_required

# Show all restaurants
@app.route('/')
@app.route('/index')
@app.route('/home')
@app.route('/restaurant')
def showRestaurants():
    restaurants = Restaurant.query.order_by(Restaurant.name.asc())
    return flask.render_template('restaurants.html', restaurants = restaurants)

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
@login_required
def newRestaurant(user_):
    if request.method == 'POST':
        newRestaurant = Restaurant(name = request.form['name'], user_id=user_['user_id'])
        db.session.add(newRestaurant)
        flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        db.session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return flask.render_template('newRestaurant.html')


#Edit a restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
@login_required
def editRestaurant(restaurant_id):
    editedRestaurant = Restaurant.query.filter_by(id = restaurant_id).one()
    # if editedRestaurant.user_id != user_['user_id']:
    #     return "$(function(){    $.alert({title: 'Alert!', content: 'Simple alert!' });})"
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            db.session.commit()
            flash('Restaurant successfully renammed to: %s' % editedRestaurant.name)
            return redirect(url_for('showRestaurants'))
    else:
        return flask.render_template('editRestaurant.html', restaurant=editedRestaurant)


#Delete a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
@login_required
def deleteRestaurant(restaurant_id):
    restaurantToDelete = Restaurant.query.filter_by(id = restaurant_id).one()
    # if restaurantToDelete.user_id != user_['user_id']:
    #     return ""
    if request.method == 'POST':
        db.session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        db.session.commit()
        return redirect(url_for('showRestaurants', restaurant_id = restaurant_id))
    else:
        return flask.render_template('deleteRestaurant.html', restaurant=restaurantToDelete)


#Show a restaurant menu
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).one()
    items = MenuItem.query.filter_by(restaurant_id = restaurant_id).all()
    user_ = session['user'] if 'user' in session else {}
    return flask.render_template('menu.html', items = items, restaurant = restaurant)
     


#Create a new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new/',methods=['GET','POST'])
@login_required
def newMenuItem(restaurant_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).one()

    # # only the user who created the resturant is allowed to add a entry
    # # TODO: add a admin user
    # if restaurant.user_id != user_['user_id']:
    #     return "$(function(){    $.alert({title: 'Alert!', content: 'Simple alert!' });})"

    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], restaurant_id = restaurant_id)
        db.session.add(newItem)
        db.session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return flask.render_template('newmenuitem.html', restaurant_id = restaurant_id)


#Edit a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
@login_required
def editMenuItem(restaurant_id, menu_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).one()

    # # only the user who created the resturant is allowed to edit the entry
    # # TODO: add a admin user
    # if restaurant.user_id != user_['user_id']:
    #     return "$(function(){    $.alert({title: 'Alert!', content: 'Simple alert!' });})"

    editedItem = MenuItem.query.filter_by(id = menu_id).one()
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
        return flask.render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


#Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET','POST'])
@login_required
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).one()

    # # only the user who created the resturant is allowed to delete the entry
    # # TODO: add a admin user
    # if restaurant.user_id != user_['user_id']:
    #     return "$(function(){    $.alert({title: 'Alert!', content: 'Simple alert!' });})"

    itemToDelete = MenuItem.query.filter_by(id = menu_id).one() 
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return flask.render_template('deleteMenuItem.html', item=itemToDelete)

    