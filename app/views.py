from app import app
from flask import request, render_template, redirect, url_for
from flask.ext.paginate import Pagination
from attrdict import AttrDict
from urllib import quote_plus
import requests, json, re

import string

RESULTS_PER_PAGE = 25


@app.route('/', methods=['GET','POST'])
@app.route('/#search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        search_value = request.form.getlist('search')[0]
        search_value = quote_plus(search_value)
        print search_value # value of the search query

        result = query(search_value)

        if is_EIN(search_value):
            org = result['organization']

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

            print len(results_for_html) == 0
            pagination = Pagination(page=1, total=num_results, search=False,
                                    per_page=RESULTS_PER_PAGE)

            return render_template('index.html', results=results_for_html,
                                    pagination=pagination,
                                    no_result=len(results_for_html) == 0)

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

def get_filing_data(filing_array):
    filing_data = {'profndraising':0, 'totexpns':0}
    for filing in filing_array:
        try:
            filing_data['profndraising'] = filing['profndraising']
            filing_data['totexpns'] = filing['totexpns']
        except KeyError:
            print 'Invalid key: profndraising, totexpns'
    return filing_data

def populate_results_data(result, result_data):
    try:
        org = result['organization']
        try:
            name = org['name']
            name = name.lower()
            name = string.capwords(name)
            result_data['name'] = name
        except KeyError:
            print 'Invalid key: name'
        try:
            result_data['ntee_code'] = org['ntee_code']
        except KeyError:
            print 'Invalid key: ntee_code'
        try:
            result_data['state'] = org['state']
        except KeyError:
            print 'Invalid key: state'
        try:
            result_data['revenue'] = org['revenue_amount']
        except KeyError:
            print 'Invalid key: revenue_amount'
        try:
            result_data['nccs_url'] = org['nccs_url']
        except KeyError:
            print 'Invalid key: nccs_url'
        try:
            result_data['guidestar_url'] = org['guidestar_url']
        except KeyError:
            print 'Invalid key: guidestar_url'
        try:
            result_data['filing_data'] = get_filing_data(result['filings_with_data'])
        except KeyError:
            print 'Invalid key: filings_with_data'
    except KeyError:
        print 'Invalid key: organization'
    
        return


@app.route('/results')
def results():
    return render_template('results.html')


# TODO ? should i convert ein to <int:ein> ?
@app.route('/results/<ein>')
def ein_results(ein):
    print ein
    
    result = query(ein)

    result_data = {
        'name':'', 
        'ntee_code':0, 
        'state':'', 
        'revenue':0, 
        'nccs_url':'', 
        'guidestar_url':'', 
        'filing_data':{},
        'savings':0,
        'current_percentile':0,
        'uac_percentile':0,
        'overhead':0}

    populate_results_data(result, result_data)

    return render_template('results.html', result_data=result_data)

#@app.route('/results/') # ? results/123456789

