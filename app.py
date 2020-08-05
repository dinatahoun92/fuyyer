#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort,jsonify 
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
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
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    Do_they_seek_talent = db.Column(db.Boolean)
    talent = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String)

    
    shows = db.relationship('Show',backref='venue')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True,nullable=False)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    shows = db.relationship('Show',backref='artist')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  artist_id =db.Column(db.Integer,db.ForeignKey('Artist.id'))
  venue_id =db.Column(db.Integer,db.ForeignKey('Venue.id'))
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
  place = ''
  data = []

  for venue in Venue.query.group_by(Venue.id, Venue.city, Venue.state).all():

    if place == venue.city + venue.state:
      data[len(data) - 1]["venues"].append({
        "id": venue.id,
        "name": venue.name,
      })
      
    else:
      place = venue.city + venue.state
      data.append({
        "city": venue.city,
        "state": venue.state,
        "venues": [{
          "id": venue.id,
          "name": venue.name,
        }]
      })

  return render_template('pages/venues.html', areas=data);



@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_term = request.form.get('search_term', None)
  response = {
        "count":len(Venue.query.filter(Venue.name.ilike("%{}%".format(search_term))).all()),
        "data": Venue.query.filter(Venue.name.ilike("%{}%".format(search_term))).all()
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()
    def upcoming_shows():
        upcoming_shows = []

        for show in shows:
            if show.start_time > datetime.now():
                upcoming_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                    "start_time": show.start_time
                })
        return upcoming_shows

    # returns past shows
    def past_shows():
        past_shows = []

        for show in shows:
            if show.start_time < datetime.now():
                past_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                    "start_time":  show.start_time
                })
        return past_shows

    if venue:
      data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent":"test",
        "seeking_description": venue.talent,
        "image_link": venue.image_link,
        "past_shows": past_shows(),
        "upcoming_shows": upcoming_shows(),
        "past_shows_count": len(past_shows()),
        "upcoming_shows_count": len(upcoming_shows())
      }
      return render_template('pages/show_venue.html', venue=data)
    else:
       return render_template('errors/404.html')
     


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
  error = False
  body = {}
  try:
    form = VenueForm()
    new_venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      website=form.website_link.data,
      image_link=form.image_link.data,
      Do_they_seek_talent=form.seeking_talent.data,
      talent=form.seeking_description.data,
    )
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not b listed.')
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
      return render_template('pages/home.html')



  # on successful db insert, flash success
 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  for artist in Artist.query.all():

    data.append({
      "id": artist.id,
      "name": artist.name
    })
  
  return render_template('pages/artists.html', artists=data)
  # TODO: replace with real data returned from querying the database

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term', None)
  response = {
        "count":len(Artist.query.filter(Artist.name.ilike("%{}%".format(search_term))).all()),
        "data": Artist.query.filter(Artist.name.ilike("%{}%".format(search_term))).all()
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()

  def upcoming_shows():
    upcoming_shows = []

    for show in shows:
      if show.start_time > datetime.now():
          upcoming_shows.append({
              "artist_id": show.artist_id,
              "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
              "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
              "start_time": show.start_time
          })
    return upcoming_shows

  def past_shows():
    past_shows = []

    # if show is in past, add show details to past
    for show in shows:
        if show.start_time < datetime.now():
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                "start_time":  show.start_time
            })
    return past_shows

  if artist:
    data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "facebook_link": artist.facebook_link,
      "image_link": artist.image_link,
      "past_shows": past_shows(),
      "upcoming_shows": upcoming_shows(),
      "past_shows_count": len(past_shows()),
      "upcoming_shows_count": len(upcoming_shows())
    }
    return render_template('pages/show_artist.html', artist=data)
  else:
    return render_template('errors/404.html')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  body = {}
  try:
    form = ArtistForm()
    new_artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
    )
    db.session.add(new_artist)
    db.session.commit()
    flash('artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not b listed.')
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
      return render_template('forms/new_artist.html', form=form)
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  
  shows = Show.query.all()

  data = []

  for show in shows:
      data.append({
          "venue_id": show.venue_id,
          "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
          "artist_id": show.artist_id,
          "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
          "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
          "start_time": show.start_time
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  body = {}
  try:
    form = ShowForm()
    new_show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data,
    )
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
      return render_template('pages/home.html')

  

  # return homepage template

# error handlers


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

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
