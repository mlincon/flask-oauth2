from app import db

class Restaurant(db.Model):
    __tablename__ = 'restaurant' 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)

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

    def __repr__(self):
       return {
           'name'           : self.name,
           'description'    : self.description,
           'id'             : self.id,
           'price'          : self.price,
           'course'         : self.course,
       }
