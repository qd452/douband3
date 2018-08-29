from flask import jsonify, abort, request, make_response, render_template
from werkzeug.utils import secure_filename
from flask import Blueprint
from app.models import UserCollection, User, Movie
from app.models import usercollection_schema, usercollections_schema
from flask import redirect, url_for
import time
from app import db, celery
from app.dbcrawler.db_crawler import RoProxy, get_user_collection, \
    get_total_page_num, get_movie_detail
from flask import current_app

dbanalyst = Blueprint('dbanalyst', __name__)


@celery.task(bind=True)
def crawler_task(self, username):
    urlprefix = 'https://movie.douban.com/people/'

    print('task started!')
    u = User.query.filter_by(name=username).first()
    if not u:
        u = User(username)
        db.session.add(u)
        db.session.commit()

    db_collection_num = u.collections.count()

    baseurl = '{}{}/collect'.format(urlprefix, username)

    self.update_state(state='PROGRESS', meta={'status': 'Getting Good Proxy'})
    proxies = RoProxy()
    mv_num, pg_num, proxydct = get_total_page_num(baseurl, proxies)

    if db_collection_num < mv_num:
        self.update_state(state='PROGRESS',
                          meta={'status': 'Crawling User Collections'})
        # need to crawl
        # todo: pg_num here can be modified based on the diff btw db_collection_num & mv_num
        collection, proxydct = get_user_collection(baseurl, pg_num, proxydct)
        print('new', collection)

        u = User.query.filter_by(name=username).first()
        print(u.id)
        for col in collection:
            col['mv_url'] = col['mv_url'].rstrip('/').rsplit('/', 1)[1]
            if not UserCollection.query.filter_by(movieurl=col['mv_url'],
                                                  user_id=u.id).first():
                if not Movie.query.filter_by(url=col['mv_url']).first():
                    new_mv_patial_info = Movie(url=col['mv_url'],
                                               name=col['name'])
                    db.session.add(new_mv_patial_info)
                    db.session.commit()
                newcollection = UserCollection(u.id,
                                               col['mv_url'],
                                               col['name'],
                                               col['date_view'],
                                               col['rating_my'])
                db.session.add(newcollection)
                db.session.commit()

    collection = u.collections.all()
    print(u.collections.count())

    self.update_state(state='PROGRESS',
                      meta={'status': 'Getting User Collections from DB'})
    for c in collection:
        c.movieurl = 'https://movie.douban.com/subject/{}/'.format(c.movieurl)

    mvlist = usercollections_schema.dumps(collection, ensure_ascii=False).data

    return {'result': mvlist, 'status': 'Task completed!',
            'username': username}


@dbanalyst.route('/', methods=['GET'])
def index():
    # if request.method == 'POST':
    #     username = request.form['baseurl']  # key is name attr, not id attr
    #     app = current_app._get_current_object()
    #     task = crawler_task.apply_async(args=[username])
    #     print(task.id)
    #     print(url_for('dbanalyst.taskstatus', task_id=task.id))
    #     return render_template('base.html'), 202, {'Location': url_for('dbanalyst.taskstatus', task_id=task.id)}
    # else:
    return render_template('base.html')


@dbanalyst.route('/longtask', methods=['POST'])
def longtask():
    if request.method == 'POST':
        username = request.form['baseurl']  # key is name attr, not id attr
        app = current_app._get_current_object()
        task = crawler_task.apply_async(args=[username])
        print(task.id)
        print(url_for('dbanalyst.taskstatus', task_id=task.id))
        return jsonify({}), 202, {
            'Location': url_for('dbanalyst.taskstatus', task_id=task.id)}


@dbanalyst.route('/status/<task_id>')
def taskstatus(task_id):
    task = crawler_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            # response['result'] = task.info['result']
            response['username'] = task.info['username']
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }

    # print(response)

    return jsonify(response)


@dbanalyst.route('/user/<string:username>', methods=['POST', 'GET'])
def user(username):
    u = User.query.filter_by(name=username).first()
    if u:
        collection = u.collections.all()
        # print(u.collections.count())

        for c in collection:
            c.movieurl = 'https://movie.douban.com/subject/{}/'.format(
                c.movieurl)
        # usercollections_schema.jsonify(collection)
        # print(usercollections_schema.dumps(collection, ensure_ascii=False)[:200])
        return render_template('user.html',
                               mvlist=usercollections_schema.dumps(collection,
                                                                   ensure_ascii=False).data)
    else:
        abort(404)
