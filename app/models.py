from app import db, ma


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    collections = db.relationship('UserCollection', backref='user',
                                  lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def __init__(self, name):
        self.name = name


class UserSchema(ma.Schema):
    class Meta:
        fields = ('name',)


class UserCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateviewed = db.Column(db.String(15))
    rating_my = db.Column(db.Integer)
    moviename = db.Column(db.Text)
    movieurl = db.Column(db.String(15), db.ForeignKey('movie.url'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<UserCollection {}>'.format(self.movieurl)

    def __init__(self, user_id, movieurl, moviename, dateviewed, rating_my):
        self.user_id = user_id
        if movieurl.startswith('https://movie.douban.com/subject/'):
            movieurl = movieurl.rstrip('/').rsplit('/', 1)[1]
        self.movieurl = movieurl
        self.dateviewed = dateviewed
        self.rating_my = rating_my
        self.moviename = moviename


class UserCollectionSchema(ma.Schema):
    class Meta:
        fields = ('movieurl', 'dateviewed', 'rating_my', 'moviename')


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

class MovieSchema(ma.Schema):
    class Meta:
        fields = ('url', 'name', 'director', 'actor','genre', 'country',
                  'releasedate', 'rating')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

usercollection_schema = UserCollectionSchema()
usercollections_schema = UserCollectionSchema(many=True)

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)