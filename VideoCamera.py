import numpy as np
import cv2
global _FINISH
def videorecording():
 cap = cv2.VideoCapture(0)

 while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    print _FINISH
    # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
       break
    if _FINISH:
     cap.release()
     cv2.destroyAllWindows()
     break
