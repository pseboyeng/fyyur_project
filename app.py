#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
# import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
# from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# from flask_migrate import Migrate
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# app = Flask(__name__)
moment = Moment(app)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  areas = []
  
  city_states = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  for city_state in city_states:
    city = city_state[0]
    state = city_state[1]
    venues = Venue.query.filter_by(city=city,state=state).all()
    areas.append({
      "city":city,
      "state":state,
      "venues":venues
    })
  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.args.get('search_term')

  data = []

  venues = Venue.query.filter(Venue.name.match(search_term)).all()
  for venue in venues:
    name = venue.name
    id = venue.id
    num_upcoming_shows = venue.upcoming_shows.count()

    data.append({

    })

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.filter_by(id=venue_id).first()

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
      if request.method == 'POST':
          is_true = request.form['seeking_talent']

          if is_true == 'y':
            name = request.form['name']
            city = request.form['city']
            state = request.form['state']
            address = request.form['address']
            phone = request.form['phone']
            genres = request.form.getlist('genres[]')
            facebook_link = request.form['facebook_link']
            image_link = request.form['image_link']
            website_link = request.form['website_link']
            seeking_talent = True
            seeking_description = request.form['seeking_description']
          else:
            name = request.form['name']
            city = request.form['city']
            state = request.form['state']
            address = request.form['address']
            phone = request.form['phone']
            genres = request.form.getlist('genres[]')
            facebook_link = request.form['facebook_link']
            image_link = request.form['image_link']
            website_link = request.form['website_link']
            seeking_talent = False
            seeking_description = request.form['seeking_description']

    
      venue = Venue(
                      name=name,
                      city=city,
                      state=state,
                      address=address,
                      phone=phone,
                      genres=genres,
                      facebook_link=facebook_link,
                      image_link=image_link,
                      website_link=website_link,
                      seeking_talent=seeking_talent,
                      seeking_description=seeking_description
                      )

      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
      db.session.close()

  return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id:int):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('home.html'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term'].tolower()

  response = Artist.query.filter(Artist.name.like(search_term).tolower()).all()
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id:int):
  artist = Artist.query.filter_by(id=artist_id).first()
  if artist:
    return render_template('pages/show_artist.html', artist=artist)
  else:
    return render_template('errors/404.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id:int):
  
  form = ArtistForm()
  artist_data = Artist.query.filter_by(id=artist_id).first()

  artist = {
    'name' : artist_data.name,
    'city' : artist_data.city,
    'state' : artist_data.state,
    'phone' : artist_data.phone,
    'website_link' : artist_data.website_link,
    'facebook_link' : artist_data.facebook_link,
    'seeking_venue' : artist_data.seeking_venue,
    'seeking_description' : artist_data.seeking_description,
    'image_link' : artist_data.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id:int):
  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    test = Planet.query.filter_by(planet_name=planet_name).first()
    
    if artist:
      artist.name = request.form['name']
      artist.genres = request.form.getlist('genres[]')
      arttist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form['phone']
      artist.website_link = request.form['website_link']
      artist.facebook_link = request.form['facebook_link']
      artist.seeking_venue = request.form['seeking_venue']
      artist.seeking_description = request.form['seeking_description']
      artist.image_link = request.form['image_link']

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')

    return redirect(url_for('show_artist', artist_id=artist_id))
  finally:
    db.session.close()




@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id:int):
  form = VenueForm()

  venue_data = Venue.query.filter_by(id=venue_id).first()

  venue={
      'name' : venue_data.name,
      'genres' : venue_data.genres,
      'address' : venue_data.address,
      'city' : venue_data.city,
      'state' : venue_data.state,
      'phone' : venue_data.phone,
      'website_link' : venue_data.website_link,
      'facebook_link' : venue_data.facebook_link,
      'seeking_talent' : venue_data.seeking_talent,
      'seeking_description' : venue_data.seeking_description,
      'image_link' : venue_data.image_link
     }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id:int):

  venue = Venue.query.filter_by(id=venue_id)
  if venue:
    is_true = request.form['seeking_venue']
    if is_true == 'y':
      venue.name = request.form['name']
      venue.genres = request.form.getlist('genres[]')
      venue.address = request.form['address']
      venue.city = request.form['city']
      venue.phone = request.form['phone']
      venue.website_link = request.form['website_link']
      venue.facebook_link = request.form['facebook_link']
      venue.seeking_talent = True
      venue.seeking_description = request.form['seeking_description']
      venue.image_link = request.form['image_link']

    else:
      venue.name = request.form['name']
      venue.genres = request.form['genres[]']
      venue.address = request.form['address']
      venue.city = request.form['city']
      venue.phone = request.form['phone']
      venue.website_link = request.form['website_link']
      venue.facebook_link = request.form['facebook_link']
      venue.seeking_talent = False
      venue.seeking_description = request.form['seeking_description']
      venue.image_link = request.form['image_link']

  db.session.commit()
    
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
      if request.method == 'POST':
        is_true = request.form['seeking_venue']

        if is_true == 'y':
          name = request.form['name']
          city = request.form['city']
          state = request.form['state']
          phone = request.form['phone']
          genres = request.form.getlist('genres[]')
          facebook_link = request.form['facebook_link']
          image_link = request.form['image_link']
          website_link = request.form['website_link']
          seeking_venue = True
          seeking_description = request.form['seeking_description']
        else:
          name = request.form['name']
          city = request.form['city']
          state = request.form['state']
          phone = request.form['phone']
          genres = request.form.getlist('genres[]')
          facebook_link = request.form['facebook_link']
          image_link = request.form['image_link']
          website_link = request.form['website_link']
          seeking_venue = False
          seeking_description = request.form['seeking_description']
      
      artist = Artist(
                      name=name,
                      city=city,
                      state=state,
                      phone=phone,
                      genres=genres,
                      facebook_link=facebook_link,
                      image_link=image_link,
                      website_link=website_link,
                      seeking_venue=seeking_venue,
                      seeking_description=seeking_description
                      )

      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows = Show.query.all()
  end_time = datetime.now()

  response = []

  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)

    if show.start_time > end_time:
      data.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time
      })

  return render_template('pages/shows.html', shows=response)


@app.route('/shows/create', methods=['GET'])
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    if request.method == 'POST':
      artist_id = int(request.form['artist_id'])
      venue_id = int(request.form['venue_id'])
      start_time = request.form['start_time']
    show = Show(
                artist_id=artist_id,
                venue_id=venue_id,
                start_time=start_time
                )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
