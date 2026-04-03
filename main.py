from flask import Flask, render_template
from manager import manager_bp

app = Flask(__name__)
app.register_blueprint(manager_bp)

@app.route('/')
@app.route('/manager')
def home():
    return render_template('base_manager.html')

if __name__ == '__main__':
    app.run(debug=True)