import face_recognition
import cv2
import os

def read_img(path):
    img = cv2.imread(path)
    (h, w) = img.shape[:2]
    width = 500
    ratio = width / float(w)
    height = int(h * ratio)
    return cv2.resize(img, (width, height))



def process_video(video_path, interval_seconds, output_folder, known_faces_dir , frames):
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Load known faces and their encodings from the 'known_faces_dir'
    known_encodings = []
    known_names = []

    for file in os.listdir(known_faces_dir):
        img_path = os.path.join(known_faces_dir, file)
        img = read_img(img_path)
        face_locations = face_recognition.face_locations(img)

        if face_locations:
            img_enc = face_recognition.face_encodings(img , face_locations)[0]
            known_encodings.append(img_enc)
            known_names.append(file.split('.')[0])
        else:
            print(f"Warning: No faces detected in the image {file}.")


    saved_frame_count = 0

    for idx, (frame, timestamp) in enumerate(frames):
        print(f"Processing frame {idx + 1}/{len(frames)}")
        face_locations = face_recognition.face_locations(frame)

        if face_locations:
            frame_encodings = face_recognition.face_encodings(frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, frame_encodings):
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    match_index = matches.index(True)
                    name = known_names[match_index]
                    
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, name, (left + 2, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 2 , (0, 0, 255), 2)

            # Save the frame with detected faces
            frame_filename = os.path.join(output_folder, f"frame_{saved_frame_count:04d}_at_{timestamp:.2f}s.jpg")
            cv2.imwrite(frame_filename, frame)
            saved_frame_count += 1
            print(f"Saved frame with detected faces at {timestamp:.2f} seconds")

    print(f"Detection complete. {saved_frame_count} frames saved.")

    return saved_frame_count, output_folder
