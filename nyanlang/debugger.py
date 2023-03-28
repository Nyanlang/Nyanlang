import random

import socketio
import eventlet
import threading

class Debugger:
    def __init__(self, nyan):
        self.sio = socketio.Server(
            async_mode="eventlet",
            cors_allowed_origins="*"
        )

        self.nyan = nyan
        self.port = 0;

    def worker1(self):
        app = socketio.WSGIApp(self.sio)
        eventlet.wsgi.server(eventlet.listen(("", self.port)), app)

    def worker2(self):
        while True:
            self.send_data(self.nyan.memory)
            self.send_pointer(self.nyan.pointer)

    def run(self):
        self.port = 13896
        threading.Thread(target=self.worker1).start()
        print(f"Debugger running on port {self.port}")
        threading.Thread(target=self.worker2).start()

    def send_data(self, data):
        self.sio.emit("data", data)

    def send_pointer(self, pointer):
        self.sio.emit("pointer", pointer)

