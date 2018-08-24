from flask import Flask
from flask import render_template, flash, redirect, request
from flask import jsonify
from flask_wtf import FlaskForm
import db_craw as crawler
import time
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qudong452'

@app.route('/data')
def data():
    user = request.args.get('user') or ""
    baseurl = 'https://movie.douban.com/people/{}/collect'.format(user)
    mvlst = crawler.main(baseurl)
    mvjs = json.dumps(mvlst, ensure_ascii=False)
    return mvjs

@app.route('/', methods=['GET', 'POST'])
# @app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    form = FlaskForm()
    if form.validate_on_submit():
        # print(form)
        baseurl = request.values.get('baseurl')
        # baseurl = "https://movie.douban.com/people/JiaU_Dong/collect"
        flash('Douban Movie Profile URL {}'.format(
            baseurl))
        mvlst = crawler.main(baseurl)

        # return render_template('base.html', title='Home', user=user,
        #                    posts=posts, form=form, mvlst=mvlst)
        # return jsonify(mvlst)
        global mvjs
        mvjs = json.dumps(mvlst, ensure_ascii=False)
        return
    else:
        return render_template('base.html', title='Home', user=user,
                               posts=posts, form=form)


if __name__ == "__main__":
    app.run()
