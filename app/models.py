from app import app, db
from flask import jsonify
from magic_numbers import *

class Bucket(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	bucket_id = db.Column(db.String(BUCKET_ID_LENGTH), unique=True)

	legalfees = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	accountingfees = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	insurance = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	feesforsrvcmgmt = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	feesforsrvclobby = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	profndraising = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	feesforsrvcinvstmgmt = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	feesforsrvcothr = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	advrtpromo = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	officexpns = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	infotech = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	interestamt = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	othremplyeebene = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	totalefficiency = db.Column(db.String(PERCENTS_LENGTH), unique=False)

	def __init__(self, *args, **kwargs):
		super(Bucket, self).__init__(*args, **kwargs)

	# Takes a field_id like 'management' to compute the input value's percentile
	def get_percentile(self, field_id, value):
		# ordered array of data values parsed to floats (ignore last empty str)
		data = getattr(self, field_id).split('%')[:-1]
		# how much of the sample is covered by this interval
		interval_width = 1.0/(len(data) - 1)
		# find in which interval the input value is
		if (float(data[0]) > value):
			return 0
		for i in range(0, len(data) - 1):
			d = float(data[i])
			if value==d:
				return i*interval_width
			elif (value>d and value<float(data[i+1])):
				# percentile = number of prior intervals + half of current interval
				return (i+0.5)*interval_width
		return 1

	# Takes an array of expense percentage values and returns json list of percentiles
	# 
	def get_all_percentiles(self, this_nonprofit_expense_percent):
		percentiles_list = []
		percentages = []
		rank_of_current_nonprofit = {}
		field_names = ['othremplyeebene',
                   'feesforsrvcmgmt', 'legalfees', 'accountingfees',
                   'feesforsrvclobby', 'profndraising', 'feesforsrvcinvstmgmt',
                   'feesforsrvcothr', 'advrtpromo', 'officexpns', 'infotech',
                   'interestamt', 'insurance', 'totalefficiency']
		for name in field_names:
			rank_of_current_nonprofit[name] = self.get_percentile(name, this_nonprofit_expense_percent[name])
			#percentiles = getattr(self, name).split('%')[:-1]
			#for p in percentiles: 
			#	dict_of_values[name] = p
		return rank_of_current_nonprofit

	def get_other_nonprofit_data(self):
		field_names = ['othremplyeebene',
                   'feesforsrvcmgmt', 'legalfees', 'accountingfees',
                   'feesforsrvclobby', 'profndraising', 'feesforsrvcinvstmgmt',
                   'feesforsrvcothr', 'advrtpromo', 'officexpns', 'infotech',
                   'interestamt', 'insurance', 'totalefficiency']
		# fill expense percents
		expense_percents = {}
		for name in field_names:
			expense_percents[name] = getattr(self, name).split('%')[:-1]
		# fill rankings
		rankings = []
		interval_width = 1.0/(len(expense_percents[name]) - 1)
		for i in range(0, len(expense_percents['totalefficiency'])):
				rankings.append(i*interval_width)
		# combine the two
		other_nonprofit_data = {}
		other_nonprofit_data['expense_percents'] = expense_percents
		other_nonprofit_data['rankings'] = rankings
		return other_nonprofit_data