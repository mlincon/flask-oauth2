from app import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250))
    picture = db.Column(db.String(250))

    def __repr__(self):
       return {
           'id'      : self.id,
           'name'    : self.name,
           'email'   : self.email,
           'picture' : self.picture
       }


class Restaurant(db.Model):
    __tablename__ = 'restaurant' 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # the __repr__ method tells Python how to print objects of this class
    def __repr__(self):
       return {
           'name'         : self.name,
           'id'           : self.id,
       }
 

class MenuItem(db.Model):
    __tablename__ = 'menu_item'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), nullable = False)
    description = db.Column(db.String(250))
    price = db.Column(db.String(8))
    course = db.Column(db.String(250))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    restaurant = db.relationship('Restaurant')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
       return {
           'name'           : self.name,
           'description'    : self.description,
           'id'             : self.id,
           'price'          : self.price,
           'course'         : self.course,
       }
