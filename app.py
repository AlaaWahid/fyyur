import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

      

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #num_shows should be aggregated based on number of upcoming shows per venue.

  data=[]
  try:
    states = db.session.query(Venue.state, Venue.city).group_by(Venue.state, Venue.city).all()
    for ste in states:
      data_venue = []
      venueAll =Venue.query.filter_by(city=ste.city).all()
      for venue in venueAll:
        ven = {
          "id":venue.id,
          "name":venue.name,
          "num_upcoming_shows": Show.query.filter_by(venue_id=venue.id).count()
        }
        # append venue to data array
        data_venue.append(ven)
      vnu = {
           "state":ste.state,
           "city":ste.city,
           "venues": data_venue,
      }
      data.append(vnu)
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get("search_term", '')
  venue_result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  response = {
    "count": venue_result.count(),
    "data": venue_result
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.get(venue_id)
  ushows = db.session.query(Show).filter(Show.venue_id == venue_id,
   Show.start_time > datetime.now())
  pshows = db.session.query(Show).filter(Show.venue_id == venue_id,
  Show.start_time < datetime.now())
  venues = {
    "upcoming_shows" : [],
    "past_shows" : [],
    "id" : venue.id,
    "name" : venue.name,
    "state" : venue.state,
    "city" : venue.city,
    "address" : venue.address,
    'phone': venue.phone,
    "genres": venue.genres,
    "image_link": venue.image_link,
    "facebook_link" : venue.facebook_link,
    "seeking_talent" : venue.seeking_talent,
    "website" : venue.website
  }

  for show in ushows:
    artist = db.session.query(Artist).filter(Artist.id == show.artist_id).first()
    venues['upcoming_shows'].append({
          'artist_id': artist.id,
          'artist_name': artist.name,
          'artist_image_link' : artist.image_link,
          'start_time': str(show.start_time)
        })

  for show in pshows:
    artist = db.session.query(Artist).filter(Artist.id == show.artist_id).first()
    venues['past_shows'].append({
          'artist_id': artist.id,
          'artist_name': artist.name,
          'artist_image_link' : artist.image_link,
          'start_time': str(show.start_time)
        })
  return render_template('pages/show_venue.html', venue=venues)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion


  error=False
  name = request.form['name']
  state = request.form['state']
  city = request.form['city']
  phone = request.form['phone']
  facebook_link = request.form['facebook_link']

  venue = Venue(name=name,state=state,city=city,phone=phone,facebook_link=facebook_link)
  try:
      db.session.add(venue)
      db.session.commit()
  except:
     db.session.rollback()
    
  finally:
     db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
         flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
  else:
      # on successful db insert, flash success
       # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue_del = Venue.query.get(venue_id)
  try:
    venue_del = Venue.query.get(venue_id)
    db.session.delete(venue_del)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()  
  return None
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

    data = db.session.query(Artist).all()

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
 
  search_term = request.form.get('search_term', '')
  search = f"%{search_term}%"
  artists=Artist.query.filter(Artist.name.ilike(search)).all()
  response={}
  response['count']=len(artists)
  response['data']=artists
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artist = Artist.query.get(artist_id)
  ushows = db.session.query(Show).filter(Show.artist_id == artist_id,
    Show.start_time > datetime.now())
  pshows = db.session.query(Show).filter(Show.artist_id == artist_id,
    Show.start_time < datetime.now())
  artists = {
    "upcoming_shows" : [],
    "past_shows" : [],
    "id" : artist.id,
    "name" : artist.name,
    "state" : artist.state,
    "city" : artist.city,
    'phone': artist.phone,
    "genres": artist.genres,
    "image_link": artist.image_link,
    "facebook_link" : artist.facebook_link,
    "website" : artist.website
  }

  for show in ushows:
    venue = db.session.query(Venue).filter(Venue.id == show.venue_id).first()
    artists['upcoming_shows'].append({
          'venue_id': venue.id,
          'venue_name': venue.name,
          'venue_image_link' : venue.image_link,
          'start_time': str(show.start_time)
        })

  for show in pshows:
    venue = db.session.query(Venue).filter(Venue.id == show.venue_id).first()
    artists['past_shows'].append({
          'venue_id': venue.id,
          'venue_name': venue.name,
          'venue_image_link' : venue.image_link,
          'start_time': str(show.start_time)
        })
  return render_template('pages/show_artist.html', artist=artists)



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id>
 
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist:
    form.name.data = artist.name
    form.state.data = artist.state
    form.city.data = artist.city
    form.genres.data = artist.genres
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.website.data = artist.website
  return render_template('forms/edit_artist.html', form=form, artist=artist)

  

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get["name"]
    artist.state = request.form.get["state"]
    artist.city = request.form.get["city"]
    artist.phone = request.form.get["phone"]
    artist.genres = request.form.get["genres"]
    artist.website = request.form.get["website"]
    artist.image_link = request.form.get["image_link"]
    artist.facebook_link = request.form.get["facebook_link"]
    artist.seeking_description = request.form.get["seeking_description"]
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))
 
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
   # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form = VenueForm()
  if venue:
    form.name.data = venue.name
    form.state.data = venue.state
    form.city.data = venue.city
    form.genres.data = venue.genres
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
    form.address.data = venue.address
  return render_template('forms/edit_venue.html', form=form, venue=venue)
 
 

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
   # venue record with ID <venue_id> using the new attributes
  ven = Venue.query.get(venue_id)
  try:
    ven.name = request.form.get['name']
    ven.state = request.form.get['state']
    ven.city = request.form.get['city']
    ven.phone = request.form.get['phone']
    ven.address = request.form.get['address']
    ven.genres = request.form.get['genres']
    ven.facebook_link = request.form.get['facebook_link']
    ven.image_link = request.form.get['image_link']
    ven.website = request.form.get['website']
    ven.seeking_description = request.form.get['seeking_description']
    ven.seeking_talent = request.form.get['seeking_talent']
    db.session.add(ven)
    db.session.commit()
  except:
    db.session.rollback
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  error=False
  name = request.form['name']
  state = request.form['state']
  city = request.form['city']
  phone = request.form['phone']
  facebook_link = request.form['facebook_link']
  artist = Artist(name=name,state=state,city=city,phone=phone,facebook_link=facebook_link)
  try:
      db.session.add(artist)
      db.session.commit()
  except:
     db.session.rollback()
  finally:
     db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form["name"] + ' could not be listed.')
  else:
      # on successful db insert, flash success
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  show_route = db.session.query(Show).join(Venue).join(Artist).all()
  data = []
  for show in show_route:
      data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
      })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  
    error=False
    artist_id= request.form["artist_id"]
    venue_id= request.form["venue_id"]
    start_time = request.form["start_time"]
    show = Show(venue_id=venue_id,
            artist_id=artist_id,
            start_time =start_time)
    try:
      db.session.add(show)
      db.session.commit()
    except:
     db.session.rollback()
    
    finally:
     db.session.close()
    if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
    else:    
      # on successful db insert, flash success
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('Show was successfully listed!')
      return render_template('pages/home.html')



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
