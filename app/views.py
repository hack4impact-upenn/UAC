from app import app
from flask import request, render_template, redirect, url_for
from attrdict import AttrDict
from urllib import quote_plus
import requests, json, re

RESULTS_PER_PAGE = 25

@app.route('/', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        search_value = request.form.getlist('search')[0]
        search_value = quote_plus(search_value)
        print search_value

        result = query(search_value)

        if is_EIN(search_value):
          # ein = parse_EIN(search_value)
          org = result['organization']
          print org['name']
          print org['ein']
          print org['city']
          print org['state']
          print org['tax_period']

          # redirect
          return redirect(url_for('results'))

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
    #print "is EIN"
    query = 'https://projects.propublica.org/nonprofits/api/v1/organizations/'

    result = requests.get(query + search_value + '.json').content

  else:
    query = 'https://projects.propublica.org/nonprofits/api/v1/search.json?q='
    # TODO error checking
    result = requests.get(query + search_value).content
    
  result = json.loads(result) # convert to json obj
  return result

def is_EIN(search_value):
  # TODO double check error logic
  # 1. strip non-alphanumeric, check is number and length <= 9
  # remove all non-alphanumeric characters
  check_val = re.sub(r'[^a-zA-Z0-9]','', search_value)
  if (not check_val.isdigit()) or (len(check_val) > 9):
    return False

  # pad with leading 0's if len < 9
  if len(check_val) < 9:
    check_val = check_val.zfill(9)

  # 2. check if ein is valid using API request


  return True

@app.route('/results')
def results():
  return render_template('results.html')
