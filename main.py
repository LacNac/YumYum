from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/Manager')
def home():
    return render_template('base_manager.html')

if __name__ == '__main__':
    app.run(debug=True)