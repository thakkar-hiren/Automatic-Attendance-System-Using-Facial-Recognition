import cv2
def createdataset(enr):
    faceCascade = cv2.CascadeClassifier('Face/Cascades/haarcascade_frontalface_default.xml')
    video_cap = cv2.VideoCapture(0)

    # For each student, enter enrollment no.
    face_id = enr
    print("\n [INFO] Initializing face capture. Look the camera and wait ...")

    # count variable for face counts...
    count = 0

    while True:
        ret, frame = video_cap.read()
        # converting to gray scale..
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            # minSize=(20,20)
        )
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            count += 1
            cv2.imwrite('Face/dataset/Student.'+ str(face_id) + '.' + str(count) + '.jpg', gray[y:y+h, x:x+w])
            cv2.imshow('Video',frame)

        k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
        elif count >= 40: # Take 20 face sample and stop video
            break

    # Do a bit of cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    video_cap.release()
    cv2.destroyAllWindows()