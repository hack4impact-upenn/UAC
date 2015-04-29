from app import app, db, models
from app.models import *
from flask import request, render_template, redirect, url_for
from flask.ext.paginate import Pagination
from attrdict import AttrDict
from urllib import quote_plus
import requests, json, re


import string

RESULTS_PER_PAGE = 25

field_names = ['legalfees', 'accountingfees', 'insurance', 'feesforsrvcmgmt',
    'feesforsrvclobby', 'profndraising', 'feesforsrvcinvstmgmt', 'feesforsrvcothr',
    'advrtpromo', 'officexpns','infotech','interestamt', 'othremplyeebene']

@app.route('/', methods=['GET','POST'])
@app.route('/#search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        search_value = request.form.getlist('search')[0]
        search_value = quote_plus(search_value)
        #print search_value

        if (len(request.form.getlist('page')) > 0):
            result = query(search_value, int(request.form.getlist('page')[0]))
        else:
            result = query(search_value)

        if is_EIN(search_value):
            org = result['organization']
            # redirect
            ein = parse_EIN(search_value)
            return redirect(url_for('ein_results', ein=ein))

        else:
            filings = result['filings']
            num_results = result['total_results']

            #print 'Search yielded ' + str(num_results) + ' result(s).'

            results_for_html = []
            for i in range(0, len(filings)):
                org = filings[i]['organization']
                result_for_html = {
                    'name': org['name'],
                    'ein': org['ein'],
                    'city': org['city'],
                    'state': org['state'],
                    'tax_prd': filings[i]['tax_prd']
                }
                results_for_html.append(result_for_html)

                # print org['name']
                # print org['ein']
                # print org['city']
                # print org['state']
                # print filings[i]['tax_prd']
                # print ''

            print len(results_for_html) == 0
            if (len(request.form.getlist('page')) > 0):
                page = int(request.form.getlist('page')[0])
            else:
                page = 1
            pagination = Pagination(page=page, total=num_results, search=False,
                                    per_page=RESULTS_PER_PAGE)

            return render_template('index.html', results=results_for_html,
                                    pagination=pagination,
                                    no_result=len(results_for_html) == 0,
                                    search_value=search_value)

    return render_template('index.html')

# if search value is EIN, use Organization Method
# else, use Search Method
def query(search_value, page=0):
    # use pattern matching to check if search value is EIN or org name
    if is_EIN(search_value):
        #print "is EIN"
        query = 'https://projects.propublica.org/nonprofits/api/v1/organizations/'
        result = requests.get(query + search_value + '.json?page=' + str(page)).content

    else:
        query = 'https://projects.propublica.org/nonprofits/api/v1/search.json?q='
        # TODO error checking
        result = requests.get(query + search_value + '&page=' + str(page)).content

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

def get_pdf_url(result):
    max_year = 0
    pdf_url = ""
    try:
        filings = result['filings_with_data']
        for filing in filings:
            if filing['tax_prd'] > max_year:
                max_year = filing['tax_prd']
                pdf_url = filing['pdf_url']
    except KeyError:
        print 'Invalid Key: get_pdf_url() filings_with_data'
    try:
        filings = result['filings_without_data']
        for filing in filings:
            if filing['tax_prd'] > max_year:
                max_year = filing['tax_prd']
                pdf_url = filing['pdf_url']
    except KeyError:
        print 'Invalid Key: get_pdf_url() filings_without_data'

    return pdf_url

def populate_results_data(result, result_data, ein):
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
            #result_data['nccs_url'] = org['nccs_url']
            result_data['nccs_url'] = "http://nccsweb.urban.org/communityplatform/nccs/organization/profile/id/" + ein + "/"
        except KeyError:
            print 'Invalid key: nccs_url'
        try:
            #result_data['guidestar_url'] = org['guidestar_url']
            result_data['guidestar_url'] = "https://www.guidestar.org/organizations/"+ str(ein)[0:2]+"-" + str(ein)[2:]+"/.aspx"
        except KeyError:
            print 'Invalid key: guidestar_url'
        try:
            result_data['filing_data'] = get_filing_data(result['filings_with_data'])
        except KeyError:
            print 'Invalid key: filings_with_data'
        try:
            result_data['pdf_url'] = get_pdf_url(result)
        except KeyError:
            print 'Invalid key: pdf_url'
    except KeyError:
        print 'Invalid key: organization'
    
        return


@app.route('/results')
def results():
    return render_template('results.html', expenses=field_names)


# TODO ? should i convert ein to <int:ein> ?
@app.route('/results/<ein>')
def ein_results(ein):
    #print ein
    
    result = query(ein)

    result_data = {
        'name':'', 
        'ntee_code':0, 
        'state':'', 
        'revenue':0, 
        'nccs_url':'', 
        'guidestar_url':'', 
        'pdf_url':'',
        'filing_data':{},
        'savings':0,
        'current_percentile':0,
        'uac_percentile':0,
        'overhead':0}

    populate_results_data(result, result_data, ein)

    return render_template('results.html', result_data=result_data, expenses=field_names)

@app.route('/calculate', methods=['POST'])
def calculate():
    print request.form

    print request.form.getlist('total_revenue')
    total_rev = float(request.form.getlist('total_revenue')[0])
    print 'POST: calculating percentiles'
    expense_dict = {}
    # converts all expenses into percentages and puts into dict by category name
    for x in field_names:
        expense_dict[x] = float(request.form.getlist(x)[0]) / total_rev * 100

    state_id = request.form.getlist('state_id')[0]
    ntee_id = request.form.getlist('ntee_id')[0]
    revenue_id = request.form.getlist('revenue_id')[0]
    query_bucket_id = state_id + '_' + ntee_id + '_' + revenue_id
    table_row = models.Bucket.query.filter_by(bucket_id=query_bucket_id).first()
    return table_row.get_all_percentiles(expense_dict)

@app.route('/contact', methods=['POST'])
def contact():
    print 'HI'
    print 'arman'
    print request.form
    client_name = request.form['name']
    client_org = request.form['org']
    client_email = request.form['email']
    client_phone = request.form['phone']
    print client_name
    print client_org
    print client_email
    print client_phone

    return "200"

    # return render_template('results.html', 
    #     name=result_data['name'],
    #     ntee_code=result_data['ntee_code'],
    #     state=result_data['state'],
    #     revenue=result_data['revenue'],
    #     nccs_url=result_data['nccs_url'],
    #     guidestar_url=result_data['guidestar_url'],
    #     savings=0,
    #     current_percentile=0,
    #     uac_percentile=0,
    #     overhead=0)

    # return render_template('results.html', 
    #     name=result_data['name'],
    #     ntee_code=result_data['ntee_code'],
    #     state=result_data['state'],
    #     revenue=result_data['revenue'],
    #     nccs_url=result_data['nccs_url'],
    #     guidestar_url=result_data['guidestar_url'],
    #     savings=0,
    #     current_percentile=0,
    #     uac_percentile=0,
    #     overhead=0)

#@app.route('/results/') # ? results/123456789
