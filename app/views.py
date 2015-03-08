from app import app
from flask import request, render_template
import requests

@app.route('/', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        search_value = request.form.getlist('search')[0]
        print search_value

    print requests.get('https://projects.propublica.org/nonprofits/api/v1/search.json?q=propublica').content

    return render_template('index.html')

@app.route('/results')
def results():
    return "Output results for the current nonprofit"
