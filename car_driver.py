# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 14:36:24 2019

@author: Steven
"""
import serial
import numpy as np
import cv2
import socketserver
import sys


# arduino control using serial com
#pass in the 
class RCControl(object):

    def __init__(self, serial_port):
        self.serial_port = serial.Serial(serial_port, 115200, timeout=1)

    def steer(self, direction):
        if direction == 2:
            self.serial_port.write(b'1')
            print("Forward")
        elif direction == 0:
            self.serial_port.write(b'7')
            print("Left")
        elif direction == 1:
            self.serial_port.write(b'6')
            print("Right")
        elif direction== 3:
            self.serial_port.write(b'2')
            print("Reverse")
        else:
            self.stop()

    def stop(self):
        self.serial_port.write(b'0')
        
        
class VideoStreamHandler(socketserver.StreamRequestHandler):
    
    #initalize radio control
    rc_car = RCControl("COM4") 

    # cascade classifiers
    def handle(self):

        stream_bytes = b' '
        
        try:
            # stream video frames one by one
            while True:
                stream_bytes += self.rfile.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]

                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                   
                    cv2.imshow('image', image)
                    # cv2.imshow('mlp_image', roi)
                    
                    #do something with car right here
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print('system stopped')
                        self.rc_car.stop()
                        break
        finally:
            cv2.destroyAllWindows()
            
            sys.exit()
            exit()

class Server(object):
    def __init__(self, host, port1):
        self.host = host
        self.port1 = port1

    def video_stream(self, host, port):
        s = socketserver.TCPServer((host, port), VideoStreamHandler)
        s.serve_forever()

    def start(self):
        self.video_stream(self.host, self.port1)
        
if __name__ == '__main__':
    h, p1 = "192.168.0.35", 8000

    ts = Server(h, p1) #initiate tcp server, video streaming begins
    ts.start()
