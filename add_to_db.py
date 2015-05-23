import csv
from app import db
from app.models import *

field_names = ['legalfees', 'accountingfees', 'insurance', 'feesforsrvcmgmt',
'feesforsrvclobby', 'profndraising', 'feesforsrvcinvstmgmt', 'feesforsrvcothr',
'advrtpromo', 'officexpns','infotech','interestamt', 'othremplyeebene',
'totalefficiency']

with open('AccountingMatrixAllAllAll.csv', 'rU') as csvfile:
    reader = csv.reader(csvfile, quotechar='|')
    for row in reader:
        b = Bucket(bucket_id = row[0])
        field_counter = 1;
        for field in field_names:
            setattr(b, field, row[field_counter])
            field_counter += 1
        db.session.add(b)
db.session.commit()