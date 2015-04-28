import csv
from app import db
from app.models import *

# Drop all database tables.
db.drop_all()

# Create new database tables.
db.create_all()

field_names = ['legalfees', 'accountingfees', 'insurance', 'feesforsrvcmgmt',
'feesforsrvclobby', 'profndraising', 'feesforsrvcinvstmgmt', 'feesforsrvcothr',
'advrtpromo', 'officexpns','infotech','interestamt', 'othremplyeebene',
'totalefficiency']

with open('AccountingMatrix.csv', 'rU') as csvfile:
    reader = csv.reader(csvfile, quotechar='|')
    i = 0
    for row in reader:
    	b = Bucket(bucket_id = row[0])
    	field_counter = 1;
    	for field in field_names:
    		setattr(b, field, row[field_counter])
    		field_counter += 1
        db.session.add(b)
        i += 1
        if i%100 == 0:
            print i
db.session.commit()