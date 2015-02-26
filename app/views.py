from app import app

@app.route('/')
def search():
    return "Search for nonprofit"

@app.route('/results')
def results():
    return "Output results for the nonprofit"