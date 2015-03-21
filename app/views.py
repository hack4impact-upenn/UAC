from app import app
from flask import request, render_template
from attrdict import AttrDict
from urllib import quote_plus
import requests, json

RESULTS_PER_PAGE = 25

@app.route('/', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        search_value = request.form.getlist('search')[0]
        search_value = quote_plus(search_value)
        print search_value

        query = 'https://projects.propublica.org/nonprofits/api/v1/search.json?q='

        # TODO error checking
        result = requests.get(query + search_value).content
        result = json.loads(result) # convert to json obj

        filings = result['filings']
        num_results = result['total_results']

        for i in range(0, min(RESULTS_PER_PAGE,num_results-1)):
          org = filings[i]
          print org['organization']['name']
          print org['ein']
          print org['organization']['city']
          print org['organization']['state']
          print org['organization']['tax_period']
          print ""

    return render_template('index.html')

@app.route('/results')
def results():
    return "Output results for the current nonprofit"
