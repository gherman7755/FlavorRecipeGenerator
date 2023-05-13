from flask import Flask, render_template, request, url_for, redirect
from database_handler import DatabaseConnector

app = Flask(__name__)
con = DatabaseConnector()

@app.route("/", methods=['GET', 'POST'])
def mainpage():
    if request.method == 'POST':
        ingredient = request.form['handle_data']
        print(ingredient)
        res = con.coll.find_one({"ingredients": {"$regex": ingredient}})
        print(res)
        return render_template('index.html', search_result=res)
    else:
        return render_template('index.html')

@app.route("/about")
def alterpage():
    return "About Page"

@app.route("/handle_data", methods=[ 'POST'])
def handle_data():
    # ingredient = request.form['handle_data']
    # input_ingredients = ingredient.split()
    # con = DatabaseConnector()
    return redirect(url_for('mainpage'))

if __name__ == "__main__":
    app.run()
