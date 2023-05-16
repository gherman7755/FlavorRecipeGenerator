from flask import Flask, render_template, request, url_for, redirect
from .database_handler import DatabaseConnector

app = Flask(__name__)
con = DatabaseConnector()

@app.route("/", methods=['GET', 'POST'])
def mainpage():
    if request.method == 'POST':
        ingredient = request.form['handle_data']
        res = con.find_recipe_by_ingredient(ingredient)
        return render_template('index.html', search_result=res)
    else:
        return render_template('index.html')

@app.route("/about")
def alterpage():
    return "About Page"

@app.route("/handle_data", methods=[ 'POST'])
def handle_data():
    return redirect(url_for('mainpage'))

def runApp(db):
    app.run()
