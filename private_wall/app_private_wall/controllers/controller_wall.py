from flask import render_template, session,flash,redirect, request, url_for
import re
from flask_bcrypt import Bcrypt
from app_private_wall import app
from app_private_wall.models.model_users import User
from app_private_wall.models.model_wall import Message



@app.route('/wall',methods=['POST'])
def post_wall():

    if 'user_id' not in session:
        return redirect('/')

    sender_id = session['user_id']
    receiver_id = request.form.get('receiver_id')
    content = request.form.get('content')

    if not receiver_id or not content:
        flash("Please enter receiver and content for the message.", "error")
        return redirect(url_for('wall'))

    data = {
        "content": request.form["content"],
        "sender_id": sender_id,
        "receiver_id": receiver_id
    }
    Message.new_message(data)
    return redirect('/wall')

@app.route('/destroy/message/<int:message_id>')
def destroy_message(message_id):

    Message.delete_message(message_id)

    return redirect('/wall')