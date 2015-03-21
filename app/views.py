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

        result = query(search_value)

        if is_EIN(search_value):
          org = result['organization']
          print org['name']
          print org['ein']
          print org['city']
          print org['state']
          print org['tax_period']

        else:
          filings = result['filings']
          num_results = result['total_results']

          for i in range(0, min(RESULTS_PER_PAGE,num_results)-1):
            org = filings[i]['organization']
            print org['name']
            print org['ein']
            print org['city']
            print org['state']
            print org['tax_period']
            print ""

    return render_template('index.html')

# if search value is EIN, use Organization Method
# else, use Search Method
def query(search_value):
  # use pattern matching to check if search value is EIN or org name
  if is_EIN(search_value):
    query = 'https://projects.propublica.org/nonprofits/api/v1/organizations/'

    result = requests.get(query + search_value + '.json').content

  else:
    query = 'https://projects.propublica.org/nonprofits/api/v1/search.json?q='

    # TODO error checking
    result = requests.get(query + search_value).content
    
  result = json.loads(result) # convert to json obj
  return result

def is_EIN(search_value):
  return True

@app.route('/results')
def results():
    return "Output results for the current nonprofit"
