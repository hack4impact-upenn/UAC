from app import app
from flask import request, render_template

@app.route('/', methods=['GET','POST'])
def search():
    print "HI ARMAN"
    if request.method == 'POST':
        print "are we here at all"
        d = request.form.getlist('search')
        t = d[0]
        print t

    return render_template('index.html')

@app.route('/results')
def results():
    return "Output results for the current nonprofit"
