from app import db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean, default=True)
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'''<Venue id:{self.id} , name:{self.name} , city:{self.city} , 
        state:{self.state} , address:{self.address} , phone:{self.phone} , 
        genres:{self.genres}, image_link:{self.image_link}, facebook_link:{self.facebook_link}>'''
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    shows = db.relationship('Show', backref="artist", lazy=True)

    def __repr__(self):
        return f'''<Artist id:{self.id} , name:{self.name} , city:{self.city} , 
        state:{self.state}, phone:{self.phone} , 
        genres:{self.genres}, image_link:{self.image_link}, facebook_link:{self.facebook_link}>'''

        
# TODO: implement any missing fields, as a database migration using Flask-Migrate
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  start_time=db.Column(db.DateTime)
  artist_id =db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)

  def __repr__(self):
      return f'<Show venue_id:{self.venue_id}, artist_id:{self.artist_id}, start_time:{self.start_time}>'