#!ENV/bin/python
from app import app
# for developing use app.run(debug=True)
app.run(host='0.0.0.0', port=0)
