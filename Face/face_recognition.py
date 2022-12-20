import cv2

def Recognizer_attendance():
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    recognizer.read('Face/trainer/trainer.yml')

    faceCascade = cv2.CascadeClassifier('Face/Cascades/haarcascade_frontalface_default.xml')

    # Selecting font for printing enrollment no.
    font = cv2.FONT_HERSHEY_DUPLEX

    enrollments = []
    video_cap = cv2.VideoCapture(0)

    while True:
        ret, frame = video_cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        for(x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            enrollment, confidence = recognizer.predict(gray[y:y+h,x:x+h])
            # print("Enrollment:- ",enrollment)
            # print("Confidece:- ",confidence)
            cv2.putText(frame, str(enrollment), (x+5,y-5),font,2,(200,255,200),3)
            if enrollment not in enrollments:
                enrollments.append(enrollment)     
        cv2.imshow('camera',frame)

        k = cv2.waitKey(20) & 0xff
        if k == 27:
            break
    #print(enrollment)
    # Do cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    video_cap.release()
    cv2.destroyAllWindows()
    return enrollments