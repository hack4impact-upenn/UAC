#!flask/bin/python
import unittest
import os
from app import app, db
from app.models import *
from config import basedir

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

    def test_create_resource_type(self):
        bucket1 = Bucket(
            bucket_id = 'AL_A',
            management = '0\%1\%5\%7\%10\%')
        db.session.add(bucket1)
        db.session.commit()
        
        b = Bucket.query.filter_by(bucket_id = 'AL_A').all()
        assert len(b) == 1
        assert b[0].management == '0\%1\%5\%7\%10\%'
        assert len(Bucket.query.filter_by(bucket_id = "AL_42").all()) == 0

if __name__ == '__main__':
    unittest.main()
