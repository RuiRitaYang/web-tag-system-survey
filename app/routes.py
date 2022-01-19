import random

from app import app, db
from app.models import Users, UUIDForm
from flask import render_template, request, redirect


@app.before_request
def before_request_func():
  pass


@app.route('/', methods=['GET', 'POST'])
def index():
  uuid = None
  form = UUIDForm()
  if form.validate_on_submit():
    # TODO(@ry): check to database and record to database
    uuid = form.uuid.data
    form.uuid.data = ''
    return render_template('consent_form.html', consented=None)
  return render_template('id_validation.html', uuid=uuid, form=form)

@app.route('/consented', methods=['GET', 'POST'])
def consented():
  consent = request.form.get('consent')
  if consent == 'y':
    return render_template('background.html')
  else:
    return render_template('finish.html', finished=False)


@app.route('/tag', methods=['GET', 'POST'])
def tag():
  scenario_ids = random.sample(range(1, 20), 2)
  # TODO: stored in database
  # TODO: grab related routine information
  return render_template('tagging.html')

@app.route('/tag-submit', methods=['GET', 'POST'])
def tag_submit():
  # TODO: stored in database
  # TODO: grab related routine information
  return render_template('scenario.html')

@app.route('/scenario-submit', methods=['GET', 'POST'])
def scenario_submit():
  return render_template('easy_of_use.html')

@app.route('/eou-submit', methods=['GET', 'POST'])
def ease_of_use_submit():

  return render_template('finish.html', finished=1)

@app.route('/finish-submit', methods=['GET', 'POST'])
def finish_submit():
  if request.method == 'POST':
    email = request.form.get('email')
    interview = request.form.get('interview')
    return render_template('finish.html', finished=2)

@app.route('/db', methods=['POST', 'GET'])
def dbtests():
  if request.method == 'POST':
    uid = request.form['uid']
    new_user = Users(uid=uid)
    # Push to database
    try:
      db.session.add(new_user)
      db.session.commit()
      return redirect('/db')
    except Exception as e:
      return "Error for storing new user info:" + str(e)
  else:
    users = Users.query.order_by(Users.date_added)
    return render_template('db_test.html', users=users)
