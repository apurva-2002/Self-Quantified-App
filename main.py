from flask import Flask
from flask import render_template, request, redirect, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////G:/try1/backend/database.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
app.config['SECRET_KEY'] = 'random'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/error_page/Error'

from database import *


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        usernm = request.form.get('username')
        password = request.form.get('paswrd')
        gender = request.form.get('gender')
        if usernm not in [i.username for i in User.query.all()]:
            new_user = User(username=usernm,
                            name=name,
                            password=password,
                            gender=gender)
            db.session.add(new_user)
            db.session.commit()

            return login()
        return redirect('/error_page/Username already exists')
    return render_template('new_user_signup.html')


@app.route('/login')
def login():
    return render_template("home_page_login.html")


@app.route('/login', methods=['POST'])
def login_post():
    uname = request.form.get('username')
    passd = request.form.get('password')
    us = User.query.filter_by(username=uname).first()
    if not us:
        return render_template("home_page_login.html", error="NO such user")
    if us and us.password == passd:
        login_user(us)
        return main()
    else:
        return render_template("home_page_login.html", error="wrong password")


@app.route('/home/add', methods=['GET', 'POST'])
@login_required
def tracker_add():
    if request.method == 'POST':
        us_id = current_user.get_id()
        name = request.form.get('name')
        descript = request.form.get('description')
        type = request.form.get('type')
        us = [u.tracker_name for u in User.query.get(us_id).trackers]
        if name in us:
            return error_page('Tracker already exists')

        add = Tracker(user_id=us_id,
                      tracker_name=name,
                      description_tracker=descript,
                      type=type)

        db.session.add(add)
        db.session.commit()
        return render_template('user_home.html', user=current_user)
    return render_template('tracker_add.html', user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return login()


@app.route("/error_page/<error>")
def error_page(error):
    return render_template('error_page.html', error=error)


@app.route('/home')
@login_required
def main():
    return render_template('user_home.html', user=current_user)


@app.route('/home/<int:tracker_id>', methods=['GET', 'POST'])
@login_required
def tracker_view(tracker_id):
    t = db.session.query(Tracker.tracker_id).all()
    if (tracker_id, ) not in t:
        return error_page('No such tracker')
    track = Tracker.query.get(tracker_id)
    tlog = Log.query.filter(Log.tracker_id == Tracker.tracker_id).order_by(
        Log.date_time)
    return render_template('tracker_homepage.html', tracker=track)


@app.route('/home/<int:tracker_id>/log', methods=['GET', 'POST'])
@login_required
def log_add(tracker_id):
    if (tracker_id, ) not in db.session.query(Tracker.tracker_id).all():
        return error_page('No such tracker')
    t = Tracker.query.get(tracker_id)
    if request.method == 'POST':
        value = request.form.get('typelog')
        date_time = datetime.strptime(request.form.get("dateandtime"),
                                      '%d/%m/%Y, %H:%M:%S.%f')
        log_description = request.form.get('desc')
        l = Log(tracker_id=tracker_id,
                date_time=date_time,
                log_description=log_description,
                log=value)
        db.session.add(l)
        db.session.commit()
        return tracker_view(tracker_id)
    return render_template('log_add.html', t=t, datetime=datetime)


@app.route('/home/<int:tracker_id>/update', methods=['GET', 'POST'])
@login_required
def update_tracker(tracker_id):
    t = db.session.query(Tracker.tracker_id).all()
    if (tracker_id, ) not in t:
        return error_page('No such tracker')
    track = Tracker.query.get(tracker_id)
    if request.method == 'POST':
        track.tracker_name = request.form.get('name')
        track.description_tracker = request.form.get('description')
        track.type = request.form.get('type')
        try:
            db.session.commit()
            return main()
        except:
            db.session.rollback()

    return render_template('tracker_update.html',
                           tracker=track,
                           user=current_user)


@app.route('/home/<int:tracker_id>/delete', methods=['GET', 'POST'])
def delete_tracker(tracker_id):
    t = db.session.query(Tracker.tracker_id).all()
    if (tracker_id, ) not in t:
        return error_page("No such tracker")
    track = Tracker.query.get(tracker_id)
    try:
        db.session.delete(track)
        db.session.commit()
    except:
        db.session.rollback()
    return main()


@app.route('/log/<int:log_id>/update', methods=['GET', 'POST'])
@login_required
def update_log(log_id):
    lot = db.session.query(Log.log_id).all()
    if (log_id, ) not in lot:
        return error_page("No such log")
    l = Log.query.get(log_id)
    if request.method == 'POST':
        l.log = request.form.get("typelog")
        l.log_description = request.form.get("desc")
        l.date_time = datetime.strptime(request.form.get("dateandtime"),
                                        '%d/%m/%Y, %H:%M:%S.%f')
        try:
            db.session.commit()
            return tracker_view(l.tracker_id)
        except:
            db.session.rollback()
    return render_template('log_update.html', log=l, datetime=datetime)


@app.route('/log/<int:log_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_log(log_id):
    lot = db.session.query(Log.log_id).all()
    if (log_id, ) not in lot:
        return error_page("No such log")
    l = Log.query.get(log_id)
    db.session.delete(l)
    db.session.commit()
    return tracker_view(l.tracker_id)


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=8080)
