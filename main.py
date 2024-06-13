from flask import Flask, request, session, send_from_directory
from flask_cors import CORS, cross_origin
import os
from flask_socketio import SocketIO, emit, join_room, Namespace
import uuid

app = Flask(__name__, static_folder='dist', static_url_path='/')
app.config['SECRET_KEY'] = 'shh!'
CORS(app,resources={r"/*":{"origins":"*"}})
sio = SocketIO(app,cors_allowed_origins="*")
users = {}

class ChatRoom(Namespace):
    def __init__(self, namespace, *args, **kwargs):
        super().__init__(namespace, *args, **kwargs)
        self.rooms = {}  # room_name: owner_name

    def on_connect(self):
        room = request.args.get('room')
        name = request.args.get('name')
        session['room'] = room
        session['name'] = name
        session['avatar'] = 'https://robohash.org/' + str(uuid.uuid4())

    def on_joined(self):
        room = session.get('room')
        if room not in self.rooms:  # if room doesn't exist, create it and set owner
            self.rooms[room] = session.get('name')
            join_room(room)
            emit('status',
                 {"user": session.get('name'), "msg": ' has entered the room.', "avatar": session.get('avatar')},
                 room=room)
        else:  # if room exists, just join
            join_room(room)
            emit('status',
                 {"user": session.get('name'), "msg": ' has entered the room.', "avatar": session.get('avatar')},
                 room=room)

    def on_message(self, data):
        room = session.get('room')
        print(data)
        emit('message', {"user": session.get('name'), "msg": data['msg'], "avatar": session.get('avatar')}, room=room)

    def on_disconnect(self):
        room = session.get('room')
        emit('status', {"user": session.get('name'), "msg": ' has left the room.', "avatar": session.get('avatar')},
             room=room)
        # Remove the room from the rooms dictionary without checking if it's empty
        self.rooms.pop(room, None)
sio.on_namespace(ChatRoom('/chat'))

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/room/<id>')
def room(id):
    return send_from_directory(app.static_folder, 'index.html')



if __name__ == '__main__':
    sio.run(app, allow_unsafe_werkzeug=True)
