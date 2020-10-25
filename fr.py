import mysql.connector as con
import face_recognition
import cv2
import numpy as np
import time,datetime
import pandas as pd

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead. 
# Get a reference to webcam #0 (the default one)
def main():
    db = con.connect(host='localhost', user='root', password='root', db='attendance')
    cur = db.cursor()

    cur.execute('''SELECT picture FROM student_record''')
    data=cur.fetchall()
    print('data=',data)
    video_capture = cv2.VideoCapture(0)
    known_face_encodings=[]
    # Load a sample picture and learn how to recognize it.
    for each in data:
        faces=face_recognition.load_image_file(each[0])
        known_face_encodings.append(face_recognition.face_encodings(faces)[0])
    print("Known=",known_face_encodings)
    # Create arrays of known face encodings and their names

    cur.execute('''SELECT name FROM student_record''')
    names=cur.fetchall()
    print("Names=",names)

    known_face_names = []
    for each in names:
        known_face_names.append(each[0])

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    count=0
    col_names =  ['Name','Date','Time']
    attendance = pd.DataFrame(columns = col_names)

    face_names = []
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    print(name)
                face_names.append(name)
        face_names = list(dict.fromkeys(face_names))
        process_this_frame = not process_this_frame
        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        
        # Display the resulting image
        cv2.imshow('Video', frame)            
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

    cur.execute('''SELECT roll_no,name,semester,department FROM student_record WHERE name=%s''',[(face_names[0])])
    detail=cur.fetchall()
    print("Detail==",detail)

    ts = time.time()      
    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour,Minute,Second=timeStamp.split(":")
    
    add_detail=[]
    for each in detail:
        for i in each:
            add_detail.append(i)
    list1=["Present",date,timeStamp]
    add_detail.extend(list1)
    cur.execute('''INSERT into attendance_record(roll_no,name,semester,department,status,date,time) VALUES(%s,%s,%s,%s,%s,%s,%s)''',(add_detail[0],add_detail[1],add_detail[2],
    add_detail[3],add_detail[4],add_detail[5],add_detail[6]))
    db.commit()

main()
