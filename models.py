import dateutil.parser
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app,db)

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    address = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(10), nullable=False, unique=True)
    website_link = db.Column(db.String(), nullable=False, unique=True)
    facebook_link = db.Column(db.String(), nullable=False, unique=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text())
    image_link = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      print(f'''<Venue => name:{self.name}, 
                          genres:{self.genres}, 
                          city:{self.city}, 
                          state:{self.state}, 
                          phone:{self.phone},
                          website_link:{self.website_link},
                          facebook_link:{self.facebook_link},
                          seeking_talent:{self.seeking_talent},
                          seeking_description:{self.seeking_description},
                          image_link:{self.image_link},
                          shows:{self.shows}
                          >''')


class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(10), nullable=False, unique=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(), nullable=False, unique=True)
    image_link = db.Column(db.String())
    website_link = db.Column(db.String(), nullable=False, unique=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text())
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      print(f'''<Artist => name:{self.name},
                           city:{self.city},
                           state:{self.state},
                           phone:{self.phone},
                           genres:{self.genres},
                           facebook_link:{self.facebook_link},
                           image_link:{self.image_link},
                           website_link:{self.website_link},
                           seeking_venue:{self.seeking_venue},
                           seeking_description:{self.seeking_description},
                           shows:{self.shows}
                           >''')


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      print(f'''<Show => artist_id:{self.artist_id}, 
                         venue:{self.venue_id}, 
                         start_time:{self.start_time}
                         >''')