import cv2
import mneme
import numpy as np
import time
import quantities as pq
import termios, fcntl, sys, os
import imutils
import math
from mneme.utils.realtime_streams import pull_data
#from mneme.utils import filters


## VIEWS
class EventManager(object):

    def __init__(self,advance_command=' ',stream_start = 0,board=None):
        self.views = None
        self.view = 1
        self.numViews = 2
        self.times = None
        self.camera = CameraManager()
        self.vis = None
        self.command = advance_command
        self.events = None
        self.start = None
        self.delay = 0
        self.stream_start = stream_start
        self.board=board
        self.performance = {'actual': {}, 'predicted': {}}

    def movement(self):
        if self.views is None:
            self.views = np.asarray(['MOVEMENT'])
        else: 
            self.views = np.append(self.views,'MOVEMENT')
        
        print('Movement added')
    
    def update(self,model=None,categories=None,details=None):
        if not self.performance['actual'] and categories is not None:
            for category in categories:
                self.performance['actual'][category] = 0
                self.performance['predicted'][category] = 0



        if self.views is not None:
            if self.start is None:
                self.start = time.time()
            for view in self.views:
                if view == 'MOVEMENT':
                    event, self.performance = self.camera.OF(view=self.view,board=self.board,model=model,categories=categories,details=details,performance=self.performance)
                    if self.events is None:
                        self.times = np.asarray(time.time() - self.stream_start)
                        self.events = np.asarray(event)
                    else:
                        if len(np.shape(self.events)) == 1:
                            self.events = np.expand_dims(self.events, 1)
                        event = np.expand_dims(event, 1)
                        self.events = np.append(self.events,event,axis=1)
                        self.times = np.append(self.times, time.time() - self.stream_start)  * pq.s

                    
    def destroy(self):
        if self.camera != None:
            self.camera.cam.release()
        cv2.destroyAllWindows()


    def advance(self,key):
        if key == self.command:  # if space is pressed 
            self.view += 1
            if self.view > self.numViews:
                self.view = 0



## CAMERA
class CameraManager(object):
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.vis = None
        self.prev = self.get_frame(style='BW')

    def __del__(self):
        self.cam.release()

    def get_frame(self,style='BW'):
        success, frame = self.cam.read()
        frame = cv2.flip(frame, 1)
        # prev = imutils.resize(prev, width=800,height=600)
        if style == 'BW':
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            ret, frame= cv2.imencode('.jpg', frame)
        
        return frame

        #return prev.tobytes()
    
    def OF(self,view = 0,board=None,model=None,categories=None,details=None,performance=None):
        self.deriveFlow()
        event , performance = self.applyFlow(view,board,model,categories,details,performance)
        self.show()
        return event,performance

    def show(self,name='Mneme'):
        cv2.namedWindow(name, cv2.WINDOW_FREERATIO) 
        cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow(name, self.vis)

    
    def deriveFlow(self):
        # Derive Optical Flow from Webcam
        gray = self.get_frame(style='BW')
        self.flow = cv2.calcOpticalFlowFarneback(
            self.prev, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        self.prev = gray


    def applyFlow(self,view=0,board=None,model=None,categories=None,details=None,performance=None):
        h, w = self.prev.shape[:2]

        THRESHOLD = 5
        SIZE = 5
        STROKE = 7
        step = w/50
        x_labels = ['R','L','-']
        y_labels = ['U','D','-']

        if view == 0:
            self.vis = self.prev
        elif view == 1:
            self.vis = np.zeros((h,w,1), dtype = "uint8")

        y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2, -1).astype(int)
        fx, fy = self.flow[y, x].T
        mag = np.sqrt((fx**2) + (fy**2))
        overThresh = mag > THRESHOLD
        fx_to_draw = fx*overThresh
        x = x.astype('float32')
        x[fx_to_draw==0] = math.nan
        fx_to_draw[fx_to_draw==0] = math.nan
        y = y.astype('float32')
        fy_to_draw = fy*overThresh
        y[fy_to_draw==0] = math.nan
        lines = np.vstack([x, y, x + fx_to_draw, y + fy_to_draw]).T.reshape(-1, 2, 2)
        lines = np.int32(lines + 0.5)
        self.vis = cv2.cvtColor(self.vis, cv2.COLOR_GRAY2BGR)

        font = cv2.FONT_HERSHEY_SIMPLEX
        x_comp = []
        y_comp = []
        x_pos = []
        y_pos = []
        m = []
        for idx in range(fx.size):
            if mag[idx] > THRESHOLD-2:
                x_comp = np.append(x_comp,fx[idx])
                y_comp = np.append(y_comp,fy[idx])
                x_pos = np.append(x_pos,x[idx])
                y_pos = np.append(y_pos,y[idx])
                m = np.append(m,mag[idx])

        x_comp = np.mean(x_comp)
        y_comp = np.mean(y_comp)
        if x_comp > THRESHOLD:
            x_mov = x_labels[0]
        elif x_comp < -THRESHOLD:
            x_mov = x_labels[1]
        else: 
            x_mov = x_labels[2]

        if not performance['actual']:
            for label in x_labels:
                performance['actual'][label] = 0
        

        performance['actual'][x_mov] += 1
        
        if y_comp < -THRESHOLD:
            y_mov = y_labels[0]
        elif y_comp > THRESHOLD:
            y_mov = y_labels[1]
        else: 
            y_mov = y_labels[2]

        message = x_mov + ' | ' + y_mov


        # add flow lines to image
        if model is None:
            cv2.polylines(self.vis, lines, 0, (236, 206, 131))
        else:
            data = pull_data(board,board.rate)
            t = data[board.time_channel] *pq.s
            data = data[board.eeg_channels]
            t = t - t[0]
            details['rate'] = len(data[0])/(t[-1])
            #data = filters.butter_bandpass_filter(data, 59.0, 61.0, memory.details['rate'], order=5)
            feat,_,_,_ = mneme.utils.features.stft(data=data,t=t,t_bin=details['timebin'],rate = details['rate'],lims=(details['min_STFT'],details['max_STFT']))
            prediction = mneme.decode.predict.predict(model=model,feature=feat,categories=categories)
            if prediction == x_mov:
                cv2.polylines(self.vis, lines, 0, (236, 206, 131))
                
            else:
                cv2.polylines(self.vis, lines, 0, (131, 131, 236))

            if not performance['predicted']:
                for label in x_labels:
                    performance['predicted'][label] = 0

            performance['predicted'][prediction] += 1


        # get boundary of this text
        textsize = cv2.getTextSize(message, font, SIZE, STROKE)[0]

        # get coords based on boundary
        textX = (w - textsize[0]) / 2
        textY = (h + textsize[1]) / 2    
        
        cv2.putText(self.vis, message, (int(textX),int(textY)), font, SIZE, (236, 206, 131), STROKE, cv2.LINE_AA)
        event = [x_mov,y_mov]
        return event,performance
        


## KEYBOARD UTILITIES
def query_key():
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    try:
        key = sys.stdin.read(1)
    except IOError: pass

    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

    return key
