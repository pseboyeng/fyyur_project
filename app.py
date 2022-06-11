#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

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

  search_term = str(request.form['search_term'])
  # I got a feedback suggesting the use of ilike.
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

  data = []
  for venue in venues:
    data.append({
      'id':venue.id,
      'name':venue.name,
      'num_upcoming_shows': len(upcoming_shows)
    })

    response = {}
    response['count'] = len(data)
    response['data'] = data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id:int):

  venue = Venue.query.filter_by(id=venue_id).first()

  all_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

  shows = len(all_shows)

  if shows > 0:
    upcoming_shows = []
    for show in shows:
      artist = Artist.query.filter(Artist.id == Show.artist_id).first()

      upcoming_shows.append({
        'artist_id':artist_id,
        'artist_name':artist.name,
        'artist_image':artist.image_link
      })

    venue.upcoming_shows = upcoming_shows
    venue.upcoming_shows_count = len(upcoming_shows)

  previous_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()

  if len(previous_shows) > 0:
    shows = []

    for show in previous_shows:
      artist = Artist.query.filter(Artist.id == show.artist_id).first()

      shows.append({
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': str(show.start_time),
      })

    venue.past_shows = previous_shows
    venue.past_shows_count = len(previous_shows)

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
    venue = Venue()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']

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
  venue = Venue.filter_by(id=venue_id).first()
  try:
    if venue:
      db.session.delete(venue)
      db.session.commit()
      flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')
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

  search_term = str(request.form['search_term'])

  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()

  data = []

  for artist in artists:
    upcoming_shows = Artist.query.filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()

    data.append({
      'id': artist.id,
      'name':artist.name,
      'num_upcoming_shows':len(upcoming_shows)
    })

    response = {
      'data': data,
      'count':len(artists)
    }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id:int):
  artist = Artist.query.filter_by(id=artist_id).first()
  if artist:
    past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist.id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id== artist.id).filter(Show.start_time < datetime.now()).count()

    return render_template('pages/show_artist.html', artist=artist)
  else:
    return render_template('errors/404.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id:int):
  
  artist = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm()

  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id:int):
  form = ArtistForm(request.form)
  try:
      name = request.form['name']
      genres = request.form.getlist('genres')
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      website_link = request.form['website_link']
      facebook_link = request.form['facebook_link']
      seeking_venue = True if 'seeking_venue' in request.form else False
      seeking_description = request.form['seeking_description']
      image_link = request.form['image_link']

      artist = Artist.query.filter_by(id=artist_id).first()
   
      artist.name = name
      artist.genres = genres
      artist.city = city
      artist.state = state
      artist.phone = phone
      artist.website_link = website_link
      artist.facebook_link = facebook_link
      artist.seeking_venue = seeking_venue
      artist.seeking_description = seeking_description
      artist.image_link = image_link
      
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
      db.session.rollback()
      flash('An error occurred. Artist  could not be updated.')
  finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))




@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id:int):
  
  venue_data = Venue.query.filter_by(id=venue_id).first()
  form = VenueForm()

  form.name.data = venue_data.name
  form.genres.data = venue_data.genres
  form.address.data = venue_data.address
  form.city.data = venue_data.city
  form.state.data = venue_data.state
  form.phone.data = venue_data.phone
  form.website_link.data = venue_data.website_link
  form.facebook_link.data = venue_data.facebook_link
  form.seeking_talent.data = venue_data.seeking_talent
  form.seeking_description.data = venue_data.seeking_description
  form.image_link.data = venue_data.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id:int):

  try:
      name = request.form['name']
      genres = request.form.getlist('genres')
      address = request.form['address']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      website_link = request.form['website_link']
      facebook_link = request.form['facebook_link']
      seeking_talent = True if 'seeking_talent' in request.form else False
      seeking_description = request.form['seeking_description']
      image_link = request.form['image_link']

      venue = Venue.query.filter_by(id=venue_id).first()

      venue.name = name
      venue.genres = genres
      venue.address = address
      venue.city = city
      venue.state = state
      venue.phone = phone
      venue.website_link = website_link
      venue.facebook_link = facebook_link
      venue.seeking_talent = seeking_talent
      venue.seeking_description = seeking_description
      venue.image_link = image_link

      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue  could not be updated.')
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
  try:
    artist = Artist()
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']

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

  response = []

  for show in shows:
    response.append({
      'venue_id':show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time
    })

  return render_template('pages/shows.html', shows=response)


@app.route('/shows/create', methods=['GET'])
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    show = Show()
    show.artist_id = int(request.form['artist_id'])
    show.venue_id = int(request.form['venue_id'])
    show.start_time = request.form['start_time']

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
