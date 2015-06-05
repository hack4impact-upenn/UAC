#!ENV/bin/python
from app import app
# for developing use app.run(debug=True)
app.run(host='127.0.0.1')
