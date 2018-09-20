import os
import numpy as np
import time
import picamera
from picamera.array import PiMotionAnalysis

class GestureDetector(PiMotionAnalysis):
    QUEUE_SIZE = 12 # the number of consecutive frames to analyze
    THRESHOLD = 0.1 # the minimum average motion required in either axisglobal counter

    def __init__(self, camera):
        super(GestureDetector, self).__init__(camera)
        self.x_queue = np.zeros(self.QUEUE_SIZE, dtype=np.float)
        self.y_queue = np.zeros(self.QUEUE_SIZE, dtype=np.float)
        self.last_move = ''

    def analyze(self, a):
        global counter
        # Roll the queues and overwrite the first element with a new
        # mean (equivalent to pop and append, but faster)
        self.x_queue[1:] = self.x_queue[:-1]
        self.y_queue[1:] = self.y_queue[:-1]
        self.x_queue[0] = a['x'].mean()
        self.y_queue[0] = a['y'].mean()
        # Calculate the mean of both queues
        x_mean = self.x_queue.mean()
        y_mean = self.y_queue.mean()
        # Convert left/up to -1, right/down to 1, and movement below
        # the threshold to 0
        x_move = (
            '' if abs(x_mean) < self.THRESHOLD else
            'left' if x_mean < 0.0 else
            'right')
        y_move = (
            '' if abs(y_mean) < self.THRESHOLD else
            'down' if y_mean < 0.0 else
            'up')
        # Update the display
        movement = ('%s %s' % (x_move, y_move)).strip()
        if movement != self.last_move:
            self.last_move = movement
            # If there is a movement, increment the counter
            if movement:
                counter+=1
                

with picamera.PiCamera(resolution='VGA', framerate=30) as camera:
    with GestureDetector(camera) as detector:
        #Save the video
        camera.start_recording('video.h264', motion_output=detector)
        try:
                print("Taking Video")
                # Initialize a vector
                stack = [0]*12
                timer = [0]*12
                # Count the number of cars every 5 seconds
                for x in range(0, 12):
                    counter = 0;
                    start = time.time()
                    camera.wait_recording(5)
                    end = time.time()
                    elapsed = end - start
                    timer[x] = elapsed*(x+1)
                    timer[x] = round(timer[x],2)
                    stack[x] = counter
        finally:
            camera.stop_recording()
            # Output this data to a text file
            f = open('data.txt', 'w')
            f.writelines(str(stack))
            seq=["\n"]
            f.writelines(seq)
            f.writelines(str(timer))
            f.writelines(seq)
            f.close()
            print("Done")
            print("There are %d cars observed") %sum(stack)


