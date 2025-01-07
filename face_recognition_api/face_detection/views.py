from django.http import JsonResponse
from django.views import View
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .models import ProcessedVideo
from .face_recognition_model import process_video  # Import your process_video function
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
import cv2

@method_decorator(csrf_exempt, name='dispatch')
class VideoUploadView(View):
    def post(self, request, *args, **kwargs):
        # Get the video file and location data from the request
        video_file = request.FILES.get('video_file')
        location_longitude = request.POST.get('location_longitude')
        location_latitude = request.POST.get('location_latitude')

        # Validate that the video and location data are provided
        if not video_file or not location_longitude or not location_latitude:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Save the uploaded video file
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT,'videos'))
        video_path = fs.save(video_file.name , video_file)
        video_path = os.path.join(settings.MEDIA_ROOT, 'videos' , video_file.name)
        video_url = fs.url(video_path)

        def video_to_frames(video_path, interval_seconds):
            frames = []
            cap = cv2.VideoCapture(video_path)
            print(f"Attempting to open video file at: {os.path.abspath(video_path)}")
            if not cap.isOpened():
                print("Error: Unable to open video file.")
                return []

            fps = cap.get(cv2.CAP_PROP_FPS)  # Get FPS of the video
            video_duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)

            for timestamp in range(0, video_duration, interval_seconds):
                frame_position = int(timestamp * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
                ret, frame = cap.read()

                if ret:
                    frames.append((frame, timestamp)) 
                    print(f"Frame captured at {timestamp:.2f} seconds")
                else:
                    print(f"Could not capture frame at {timestamp:.2f} seconds")

            cap.release()
            print(frames)
            return frames

        frame = video_to_frames(video_path=video_path , interval_seconds=1)

        # Process the video to detect faces
        known_faces_dir = os.path.join(settings.MEDIA_ROOT, 'known_faces')
        output_folder = os.path.join(settings.MEDIA_ROOT, 'detected_frames')  # Define output folder for processed frames
        saved_frame_count, processed_folder = process_video(video_path, interval_seconds=1, output_folder=output_folder , known_faces_dir = known_faces_dir , frames = frame)

        # Store the video information in the database
        processed_video = ProcessedVideo(
            video_file=video_path,
            location_longitude=location_longitude,
            location_latitude=location_latitude,
            processed_frames_path=processed_folder
        )
        processed_video.save()

        # Return the response to the user
        return JsonResponse({
            'message': 'Video uploaded and processed successfully.',
            'processed_frame_count': saved_frame_count,
            'video_url': video_url,
            'processed_frames_path': processed_folder
        })
