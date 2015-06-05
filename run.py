#!ENV/bin/python
from app import app
# for developing use app.run(debug=True)
app.run(host='https://evening-shelf-8186.herokuapp.com')
