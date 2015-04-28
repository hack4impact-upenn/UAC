from app import app, db
from flask import jsonify
from magic_numbers import *

field_names = ['legalfees', 'accountingfees', 'insurance', 'feesforsrvcmgmt',
'feesforsrvclobby', 'profndraising', 'feesforsrvcinvstmgmt', 'feesforsrvcothr',
'advrtpromo', 'officexpns','infotech','interestamt', 'othremplyeebene']

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
		# prepend data array with value of percentile 0
		data = [0] + data
		# how much of the sample is covered by this interval
		interval_width = 1.0/(len(data))
		# find in which interval the input value is
		for i in range(0, len(data)):
			d = float(data[i])
			if value==d:
				return i*interval_width
			elif (i==len(data)-1) or (value>d and value<float(data[i+1])):
				# percentile = number of prior intervals + half of current interval
				return (i+0.5)*interval_width

	# Takes an array of expense percentage values and returns json list of percentiles
	# 
	def get_all_percentiles(self, expense_dict):
		percentiles_list = []
		percentages = []
		arr = {}
		for (name in field_names):
			percentile_for_this_value = self.get_percentile(name, expense_dict[name])
			arr[name].append(percentile_for_this_value)
			percentiles = getattr(self, name).split('%')[:-1]
			for p in percentiles: 
				arr[name].append(p)

		return jsonify(
			legalfees_array=arr['legalfees_array'],
			accountingfees_array=arr['accountingfees_array'],
			insurance_array=arr['insurance_array'],
			feesforsrvcmgmt_array=arr['feesforsrvcmgmt_array'],
			feesforsrvclobby_array=arr['feesforsrvclobby_array'],
			profndraising_array=arr['profndraising_array'],
			feesforsrvcinvstmgmt_array=arr['feesforsrvcinvstmgmt_array'],
			feesforsrvcothr_array=arr['feesforsrvcothr_array'],
			advrtpromo_array=arr['advrtpromo_array'],
			officexpns_array=arr['officexpns_array'],
			infotech_array=arr['infotech_array'],
			interestamt_array=arr['interestamt_array'],
			othremplyeebene_array=arr['othremplyeebene_array'],
			totalefficienc_array=arr['totalefficienc_array'],
			percentages=percentages,
			list=percentiles_list,
			values=values)