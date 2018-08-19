from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    collections = db.relationship('UserCollection', backref='user',
                                  lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.name)


class UserCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateviewed = db.Column(db.String(15))
    movieurl = db.Column(db.String(15), db.ForeignKey('movie.url'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<UserCollection {}>'.format(self.body)


class Movie(db.Model):
    url = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.Text)
    director = db.Column(db.Text)
    actor = db.Column(db.Text)
    genre = db.Column(db.Text)
    country = db.Column(db.Text)
    releasedate = db.Column(db.String(15))
    rating = db.Column(db.Text)

    def __repr__(self):
        return '<Movie {}-{}>'.format(self.name, self.url)
