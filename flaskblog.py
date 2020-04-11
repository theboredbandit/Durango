from flask import Flask,render_template, url_for
app = Flask(__name__)

posts=[
	{
		'author':'Suryansh',
		'title':'post 1',
		'date_posted':'12/04/2020'
	},
	{
		'author':'Lalli',
		'title':'post 2',
		'date_posted':'16/04/2020'	
	}
]
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)
@app.route("/home/about")
def about():
	return render_template('about.html',title='About')

if __name__=='__main__':
	app.run(debug=True)