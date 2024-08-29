from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'notforproduction'
socketio = SocketIO(app)

rooms = {}
tets = {}

def generate_unique_code(length):
    while True:
        code = ''
        for _ in range(length):
            code += random.choice(ascii_uppercase)      
        if code not in rooms:
            break  
    return code


# ROUTES
@app.route('/', methods=['POST', 'GET'])
def home():
    session.clear()
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code').upper()
        join = request.form.get('join', False)
        create = request.form.get('create', False)
        if not name:
            return render_template('home.html', error='Please enter your unique chat name', code='code', name='name')
        
        if join != False and not code:
            return render_template('home.html', error='Please enter the code for chatroom you want to join')
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {'members': [], 'messages': []}
        elif code not in rooms:
            return render_template('home.html', error='Chatroom does not exist')

        if code and name in rooms[room]['members']:
            return render_template('home.html', error='The name you chose is already in use for the chatroom you want to join')
        session['room'] = room
        session['name'] = name
        return redirect(url_for('room'))
    return render_template('home.html')


@app.route('/room')
def room():
    room = session.get('room')
    if room is None or session.get('name') is None or room not in rooms:
        return redirect(url_for('home'))
    return render_template('room.html', code=room, messages=rooms[room]['messages'])


# SocketIO
@socketio.on('message')
def message(data):
    room = session.get('room')
    if room not in rooms:
        return
    now = datetime.now()
    date_created =  now.strftime('%m/%d/%Y %I:%M%p').lstrip('0').replace(' 0', ' ')
    content = {
        'name': session.get('name'),
        'message': data['data'],
        'date_created': date_created,
    }
    send(content, to=room)
    rooms[room]['messages'].append(content)
    print(f"{session.get('name')} said: {data['data']} at {content['date_created']}")


@socketio.on('connect')
def connect(auth):
    room = session.get('room')
    name = session.get('name')
    now = datetime.now()
    date_created =  now.strftime('%m/%d/%Y %I:%M%p').lstrip('0').replace(' 0', ' ')
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    send({'name': name, 'message': ' has entered the room ', 'date_created': date_created},to=room)
    rooms[room]['members'].append(name)
    print(f'{name} joined chatroom: {room}')


@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    name = session.get('name')
    now = datetime.now()
    date_created =  now.strftime('%m/%d/%Y %I:%M%p').lstrip('0').replace(' 0', ' ')
    leave_room(room)
    if room in rooms:
        rooms[room]['members'].remove(name)
        if len(rooms[room]['members']) <= 0:
            del rooms[room]
    send({'name': name, 'message': 'has left the room', 'date_created':date_created}, to=room)
    print(f'{name} has left the chatroom: {room}')


if __name__ == '__main__':
    socketio.run(app, debug=True)
