#!flask/bin/python
import unittest
import os
from app import app, db
from app.models import *
from config import basedir
import csv

class TestCase(unittest.TestCase):

    # Run at the beginning of every test.
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        self.field_names = [
            'management', 'legal', 'accounting', 'lobbying', 'fundraising',
            'investment', 'other_fees', 'advertising', 'office',
            'interest', 'insurance', 'other_benefits']
        db.create_all()

    # Run at the end of every test.
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_bucket(self):
        bucket1 = Bucket(
            bucket_id = 'AL_A',
            management = '0%1%5%7%10%')
        db.session.add(bucket1)
        db.session.commit()
        b = Bucket.query.filter_by(bucket_id = 'AL_A').all()
        assert len(b) == 1
        assert b[0].management == '0%1%5%7%10%'
        assert len(Bucket.query.filter_by(bucket_id = "AL_42").all()) == 0

    def test_get_percentile_first_interval(self):
        bucket1 = Bucket(
            bucket_id = 'AL_A',
            management = '0%1%5%7%10%')
        db.session.add(bucket1)
        db.session.commit()
        b = Bucket.query.filter_by(bucket_id = 'AL_A').first()
        # [0%] 0%, 1%, 5%, 7%, 10% [last value]
        # 5 values, 6 intervals, interval width = 16.67
        assert b.get_percentile('management', 0) == 0

    def test_get_percentile_middle_intervals(self):
        bucket1 = Bucket(
            bucket_id = 'AL_A',
            management = '0%1%5%7%10%')
        db.session.add(bucket1)
        db.session.commit()
        b = Bucket.query.filter_by(bucket_id = 'AL_A').first()
        # [0%] 0%, 1%, 5%, 7%, 10% [last value]
        # 5 values, 6 intervals, interval width = 16.67
        assert b.get_percentile('management', 1) > 33.3
        assert b.get_percentile('management', 1) < 33.4
        assert b.get_percentile('management', 3) > 41.66
        assert b.get_percentile('management', 3) < 41.67

    def test_get_percentile_last_interval(self):
        bucket1 = Bucket(
            bucket_id = 'AL_A',
            management = '0%1%5%7%10%')
        db.session.add(bucket1)
        db.session.commit()
        b = Bucket.query.filter_by(bucket_id = 'AL_A').first()
        # [0%] 0%, 1%, 5%, 7%, 10% [last value]
        # 5 values, 6 intervals, interval width = 16.67
        assert b.get_percentile('management', 1000) > 91.66
        assert b.get_percentile('management', 1000) < 91.67

    def test_read_csv(self):
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

        wy_z = Bucket.query.filter_by(bucket_id = 'WY_Z').all()
        assert len(wy_z) == 1
        assert wy_z[0].legal == '0.52%0.64%0.95%'
        ca_t = Bucket.query.filter_by(bucket_id = 'CA_T').all()
        assert len(wy_z) == 1
        assert ca_t[0].management == '0.0%0.0%0.0%0.0%0.0%0.0%0.0%0.17%0.91%'

if __name__ == '__main__':
    unittest.main()
