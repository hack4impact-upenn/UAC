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
				return i*interval_width*100
			elif (i==len(data)-1) or (value>d and value<float(data[i+1])):
				# percentile = number of prior intervals + half of current interval
				return (i+0.5)*interval_width*100

	# Takes an array of expense percentage values and returns json list of percentiles
	def get_all_percentiles(self, values):
		percentiles_list = []
		percentages = []
		for i in range(0, len(field_names)):
			percentiles_list.append(self.get_percentile(field_names[i], float(values[i])))
			percentages.append(getattr(self, field_names[i]))

		return jsonify(percentages=percentages,
			list=str(percentiles_list),
			values=values)