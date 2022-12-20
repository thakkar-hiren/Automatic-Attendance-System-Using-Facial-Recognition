import os
import cv2
import numpy as np
from PIL import Image


# Path for face image database
def traindataset():
    path1= 'Face/dataset'
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    detector = cv2.CascadeClassifier("Face/Cascades/haarcascade_frontalface_default.xml")


    def getImagesAndLabel(path):
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
        faceSamples = []
        enrollments = []
        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img,'uint8')
            enrollment = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = detector.detectMultiScale(img_numpy)
            for(x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                enrollments.append(enrollment)
        return faceSamples,enrollments

    print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    face,enrollment_no = getImagesAndLabel(path1)
    recognizer.train(face,np.array(enrollment_no))

    #Saving the Training Module...
    recognizer.write('Face/trainer/trainer.yml')

    # Print the numer of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(enrollment_no))))