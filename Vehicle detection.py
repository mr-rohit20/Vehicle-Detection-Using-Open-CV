import cv2
import numpy as np
from time import sleep

#web camera
cap = cv2.VideoCapture('video.mp4')

min_width_rectangle = 80 
min_height_rectangle = 80

count_line_pos = 550  #count line position (y-axis)

#initialize OpenCV - Background subtractor 
algo = cv2.createBackgroundSubtractorKNN()

#pick up center of bounding rectangles
def center_handle(x,y,w,h):
    x1=int(w/2)
    y1=int(h/2)
    cx= x+x1
    cy= y+y1
    return cx,cy

detect = []
offset = 6.5 #allowable error between pixel  
delay = 30  #30 Video FPS
counter =0  #vehicle counter

while True:
    ret, frame1= cap.read()

    time= float(1/delay)
    sleep(time)

    #convert an image from BGR to grayscale format
    grey = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey,(3,3),5)  #Gaussian filter for image smoothing

    # applying on each frame
    img_sub = algo.apply(blur)  #extract the MOG-method of foreground mask

    dilat = cv2.dilate(img_sub,np.ones((5,5)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    dilated = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)
    dilated = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)

    counterShape,h = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.line(frame1,(25,count_line_pos),(1200,count_line_pos), (255,127,0), 3)


    for (i,c) in enumerate(counterShape):  #keep a count of iterations
        (x,y,w,h) = cv2.boundingRect(c)
        validate_counter = (w>= min_width_rectangle) and (h>= min_height_rectangle)
        if not validate_counter:
            continue

        #draw the boundig rectangle for all  counters    
        cv2.rectangle(frame1,(x,y),(x+w,y+h),(0,255,0),2)

        center= center_handle(x,y,w,h)
        detect.append(center) #detect
        cv2.circle(frame1,center,4,(0,0,255),-1)

        for (x,y) in detect:
            if y<(count_line_pos+offset) and y>(count_line_pos-offset):
                counter+=1
                cv2.line(frame1,(25,count_line_pos),(1200,count_line_pos),(0,127,255),3) 
                detect.remove((x,y))
                print("Vehicle is detected: "+str(counter))

    cv2.putText(frame1, "VEHICLE COUNTER :"+str(counter), (450,70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 5)            
    # cv2.imshow('Detector', dilated)
    cv2.imshow("Video Original",frame1)

    if cv2.waitKey(1) == 27:
        break

#release video capture
cv2.destroyAllWindows()
cap.release()