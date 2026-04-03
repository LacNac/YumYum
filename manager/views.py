from flask import flash, redirect, render_template, url_for
from . import manager_bp
import sqlite3

@manager_bp.route('/delivery')
def delivery():
       return render_template('delivery.html')

@manager_bp.route('/eatin')
def eatin():
       return render_template('eatin.html')

@manager_bp.route('/total')
def total():
       return render_template('total.html')

@manager_bp.route('/add_prod')
def add_prod():
       return render_template('add_prod.html')

@manager_bp.route('/del_prod')
def del_prod():
       return render_template('del_prod.html')