import csv
from app import db
from app.models import *

# Drop all database tables.
db.drop_all()

# Create new database tables.
db.create_all()

field_names = ['management', 'legal', 'accounting', 'lobbying', 'fundraising',
    'investment', 'other_fees', 'advertising', 'office', 'interest',
    'insurance', 'other_benefits']

with open('AccountingMatrix.csv', 'rU') as csvfile:
    reader = csv.reader(csvfile, quotechar='|')
    for row in reader:
    	b = Bucket(bucket_id = row[0])
    	field_counter = 1;
    	for field in field_names:
    		setattr(b, field, row[field_counter])
    		field_counter += 1
        db.session.add(b)
db.session.commit()

