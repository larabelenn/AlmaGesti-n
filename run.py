# run.py
from app import app, socketio

if __name__ == '__main__':
    # Usamos socketio.run() para que el servidor sea compatible con WebSockets
    socketio.run(app, debug=True)