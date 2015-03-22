from app import app
from flask import request, render_template, redirect, url_for
from flask.ext.paginate import Pagination
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
            org = result['organization']
            print org['name']
            print org['ein']
            print org['city']
            print org['state']
            print result['tax_prd']

            # redirect
            ein = parse_EIN(search_value)
            return redirect(url_for('ein_results', ein=ein))

        else:
            filings = result['filings']
            num_results = result['total_results']

            print 'Search yielded ' + str(num_results) + ' result(s).'

            results_for_html = []
            for i in range(0, min(RESULTS_PER_PAGE,num_results)-1):
                org = filings[i]['organization']
                result_for_html = {
                    'name': org['name'],
                    'ein': org['ein'],
                    'city': org['city'],
                    'state': org['state'],
                    'tax_prd': filings[i]['tax_prd']
                }
                results_for_html.append(result_for_html)

                # print - delete me when ur done
                print org['name']
                print org['ein']
                print org['city']
                print org['state']
                print filings[i]['tax_prd']
                print ''

            pagination = Pagination(page=1, total=num_results, search=False, per_page = RESULTS_PER_PAGE)

            return render_template('index.html', results=results_for_html, pagination=pagination)

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

# TODO ? - what if they search for a number that happens to be an ein?
def is_EIN(search_value):
    # TODO double check error logic
    # 1. strip non-alphanumeric, check is number and length <= 9
    # remove all non-alphanumeric characters
    check_val = parse_EIN(search_value)
    if (not check_val.isdigit()) or (len(check_val) > 9):
        return False

    # 2. check if ein is valid using API request
    #return is_valid_EIN(check_val)
    if not is_valid_EIN(check_val):
        return False

    return True

def parse_EIN(search_value):
    ein = re.sub(r'[^a-zA-Z0-9]','', search_value)

    # pad with leading 0's if len < 9
    if len(ein) < 9:
        ein = ein.zfill(9)

    return ein

# may become deprecated if the Propublica API changes the way they handle 
# invalid EIN get requests
def is_valid_EIN(ein):
    query = 'https://projects.propublica.org/nonprofits/api/v1/organizations/'
    result = requests.get(query + ein + '.json').content

    # check if result is html page rather than valid json object
    if result.split('\n', 1)[0] == '<!DOCTYPE html>':
        return False
    return True

@app.route('/results')
def results():
    return render_template('results.html')

# TODO ? should i convert ein to <int:ein> ?
@app.route('/results/<ein>')
def ein_results(ein):
    print ein

    result = query(ein)

    org = result['organization']
    print org['name']
    print org['ein']
    print org['city']
    print org['state']
    print result['tax_prd']

    return render_template('results.html')

#@app.route('/results/') # ? results/123456789

