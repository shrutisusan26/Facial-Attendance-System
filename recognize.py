import cv2
import numpy as np
import face_recognition
import glob

all_encodings = []
all_image_names = []


def get_encodings(img,img1):
    # get the encodings of the images
    face_loc = face_recognition.face_locations(img)[0]
    encodings = face_recognition.face_encodings(img)[0]
    cv2.rectangle(img1, (face_loc[3], face_loc[0]), (face_loc[1], face_loc[2]), (255, 0, 255), 3)
    return encodings


def get_images(images):
    # Loading the image from face_recognition
    for image in images:
        img = face_recognition.load_image_file(image)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img1 = img.copy()
        all_encodings.append(get_encodings(img,img1))
        name = image.split(".")
        name = name[1].split("/")
        all_image_names.append(name[len(name) - 1])
def main():
    cap=cv2.VideoCapture(0)
    images = glob.glob("/home/shruti/dlib-19.6/images/*.jpeg")
    get_images(images)
    while True:
        #capture the images from webcam and compare their encodings
        success,img=cap.read()
        img1=img.copy()
        imgResized=cv2.resize(img,(0,0),None,0.25,0.25)
        img=cv2.cvtColor(imgResized,cv2.COLOR_BGR2RGB)
        location=face_recognition.face_locations(img)
        encodings=face_recognition.face_encodings(img,location)
        faces = []
        for enc,loc in zip(encodings,location):
            res=face_recognition.compare_faces(all_encodings,enc)
            dis=face_recognition.face_distance(all_encodings,enc)
            match=np.argmin(dis)
            if dis[match] and res[match]!=False:
                cv2.rectangle(img1,(loc[3]*4,loc[0]*4),(loc[1]*4,loc[2]*4),(255,0,255),2)
                cv2.rectangle(img1,(loc[3]*4,loc[2]*4-30),(loc[1]*4,loc[2]*4),(255,0,255),cv2.FILLED)
                cv2.putText(img1, f'{all_image_names[match].upper()},Distance={round(dis[match])}',(loc[1]*4-200,loc[2]*4-15),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),2)
                faces.append(all_image_names[match].upper())
                cv2.imshow("Result", img1)
                cv2.waitKey(1)
        if (cv2.waitKey(1) & 0xFF == ord('q')) and faces!=[]:
           # print(faces)
            cap.release()
            cv2.destroyAllWindows()
            return faces

