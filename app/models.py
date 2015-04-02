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

	def get_percentile(self, field_id):
		# ordered array of data values
		data = self.getattr(self, field_id).split('\%')
		# number of intervals 
		n = len(data) + 1
		
		return 