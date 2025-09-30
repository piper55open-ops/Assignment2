from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/locations')
def locations():
    return render_template("locations.html")

@app.route('/accommodations')
def accommodations():
    return render_template("accommodations.html")

@app.route('/stories')
def stories():
    return render_template("stories.html")

@app.route('/discover')
def discover():
    return render_template("discover.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
