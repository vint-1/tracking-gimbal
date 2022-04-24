import io
import cv2 as cv
import logging
import socketserver
from threading import Condition
from http import server
import threading

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        # if True or buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
        self.buffer.truncate()
        with self.condition:
            self.frame = self.buffer.getvalue()
            self.condition.notify_all()
        self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with MJPG_OUTPUT.condition:
                        MJPG_OUTPUT.condition.wait()
                        frame = MJPG_OUTPUT.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    timeout=0

MJPG_OUTPUT = StreamingOutput()
STREAMING_PORT = 5000

class Streamer():
    def __init__(self, host = '', port = STREAMING_PORT):
        self.address = (host, port)
        self.svr = StreamingServer(self.address, StreamingHandler)
        self.thread = threading.Thread(target=self.svr.serve_forever)
        self.thread.daemon = True

    def start_streaming(self):
        self.thread.start()
    
    def is_streaming(self):
        return self.thread.isAlive()

    def write_img(self, img):
        _, buffer = cv.imencode(".jpg", img)
        MJPG_OUTPUT.write(buffer)

if __name__ == "__main__":
    vid = cv.VideoCapture("-v v4l2src device=/dev/video0 num-buffers=-1 ! video/x-raw,width=1280,height=720, framerate=30/1 ! appsink", cv.CAP_GSTREAMER)
    fourcc = cv.VideoWriter_fourcc(*'XVID')

    streamer = Streamer()
    streamer.start_streaming()

    while vid.isOpened():
        ret, img1 = vid.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        scale_factor = 1.5
        downsized = cv.resize(img1, None, fx=1/scale_factor, fy=1/scale_factor, interpolation=cv.INTER_AREA)
        streamer.write_img(downsized)

    # with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    #     output = StreamingOutput()
    #     #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #     #camera.rotation = 90
        
        
    #     address = ('', 8000)
    #     svr = StreamingServer(address, StreamingHandler)
    #     threading.Thread(target=svr.serve_forever).start()
    #     camera.start_recording(output, format='mjpeg')
    #     while True:
    #         # svr.timeout=0
    #         # svr.handle_request()
    #         print("great success")
    #         time.sleep(5)