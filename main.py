import cv2
import face_recognition
import os
import csv
from datetime import datetime
import numpy as np

# Initialize video capture from the default camera (0)
video_capture = cv2.VideoCapture(0)

# Load known faces and names from the "known_faces" folder
known_faces = []
known_names = []

known_faces_folder = "known_faces"

for filename in os.listdir(known_faces_folder):
    if filename.endswith(".jpeg"):
        student_name = os.path.splitext(filename)[0]
        student_image = face_recognition.load_image_file(os.path.join(known_faces_folder, filename))
        student_face_encoding = face_recognition.face_encodings(student_image)
        if len(student_face_encoding) > 0:
            known_faces.append(student_face_encoding[0])
            known_names.append(student_name)

# Initialize variables for tracking attendance
attendance = set()  # Use a set to store attendees
current_date = datetime.now().strftime("%Y-%m-%d")
attendance_file = f"attendance_{current_date}.csv"

# Create or append to the attendance CSV file
if not os.path.exists(attendance_file):
    with open(attendance_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Name", "Timestamp"])

while True:
    # Capture frame from the webcam
    _, frame = video_capture.read()

    # Resize the frame for faster face recognition
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the frame from BGR (OpenCV) to RGB (face_recognition)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Find all face locations in the frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # Initialize an empty list of names for this frame
    face_names = []

    for face_encoding in face_encodings:
        # Check if face encodings are found
        if known_faces:
            # Try to match the face with known faces
            matches = face_recognition.compare_faces(known_faces, face_encoding)
            name = "Unknown"

            if True in matches:
                best_match_index = matches.index(True)
                name = known_names[best_match_index]

                # Check if the person has not already been marked as present
                if name not in attendance:
                    attendance.add(name)  # Add the person to the attendance set
                    current_time = datetime.now().strftime("%H:%M:%S")
                    with open(attendance_file, 'a', newline='') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow([name, current_time])

            face_names.append(name)

    # Display the results on the live frame
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Draw a label with the name below the face
        cv2.putText(frame, name, (left + 6, bottom + 30), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)

    # Display the resulting frame with recognized faces
    cv2.imshow("Attendance System", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close all OpenCV windows
video_capture.release()
cv2.destroyAllWindows()
