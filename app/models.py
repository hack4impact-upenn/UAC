from app import app, db
from magic_numbers import *

class Bucket(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	bucket_id = db.Column(db.String(BUCKET_ID_LENGTH), unique=True)

	management = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	legal = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	accounting = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	lobbying = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	fundraising = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	investment = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	other_fees = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	advertising = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	office = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	interest = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	insurance = db.Column(db.String(PERCENTS_LENGTH), unique=False)
	other_benefits = db.Column(db.String(PERCENTS_LENGTH), unique=False)

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
