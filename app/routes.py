from flask import Blueprint, render_template

main=Blueprint('main',__name__)

@main.route('/')
def index():
    return "<h1> Placement Portal is Running!</h1>"

