from app import app
from flask import render_template, request, session

@app.before_request
def before_request_func():
  pass

@app.route("/")
def index():
  if 'consent' in session and session['consent']:
    return render_template('index.html', consented=True)
  else:
    session.pop('consent') if 'consent' in session else None
    return render_template('index.html', consented=None)


@app.route("/consented", methods=['GET', 'POST'])
def consented():
  consent = request.form.get('consent')
  session['consent'] = (consent == 'y')
  return render_template('index.html', consented=session['consent'])
