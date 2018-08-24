from flask import jsonify, abort, request, make_response, render_template
from werkzeug.utils import secure_filename
from flask import Blueprint
from app.models import UserCollection, User, Movie
from app.models import usercollection_schema, usercollections_schema
from flask import redirect, url_for
import time
from app import db
from app.dbcrawler.db_crawler import RoProxy, get_user_collection, \
    get_total_page_num, get_movie_detail

dbanalyst = Blueprint('dbanalyst', __name__)


@dbanalyst.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        username = request.form['baseurl']  # key is name attr, not id attr
        urlprefix = 'https://movie.douban.com/people/'

        u = User.query.filter_by(name=username).first()
        if not u:
            baseurl = '{}{}/collect'.format(urlprefix, username)

            proxies = RoProxy()
            print(baseurl)
            collection, proxydct = get_user_collection(baseurl, proxies)
            print('new', collection)
            u = User(username)
            db.session.add(u)
            db.session.commit()
            u = User.query.filter_by(name=username).first()
            print(u.id)
            for col in collection:
                newcollection = UserCollection(u.id,
                                               col['mv_url'],
                                               col['name'],
                                               col['date_view'],
                                               col['rating_my'])
                db.session.add(newcollection)
                db.session.commit()

        return redirect(url_for('dbanalyst.user', username=username))
    else:
        return render_template('base.html')


@dbanalyst.route('/user/<string:username>', methods=['POST', 'GET'])
def user(username):
    u = User.query.filter_by(name=username).first()
    collection = u.collections.all()

    for c in collection:
        c.movieurl = 'https://movie.douban.com/subject/{}/'.format(c.movieurl)
    # usercollections_schema.jsonify(collection)
    # print(usercollections_schema.dumps(collection, ensure_ascii=False)[:200])
    return render_template('user.html', mvlist=usercollections_schema.dumps(collection, ensure_ascii=False).data)
