import cv2
import os

def extract_frames(video_path, out_dir, fps=3):
    """
    Extracts frames and returns metadata including EXACT timestamps.
    """
    import cv2, os

    os.makedirs(out_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    # Fallback if FPS reading fails
    if video_fps <= 0:
        video_fps = 30 

    # Calculate how many frames to skip to match desired extraction FPS
    frame_interval = int(video_fps // fps) if video_fps > fps else 1
    
    extracted_data = []
    idx = 0
    saved_count = 0

    print(f"   > Extracting frames from {os.path.basename(video_path)} (Source FPS: {video_fps})...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if idx % frame_interval == 0:
            # Calculate precise timestamp: current_frame_number / total_frames_per_second
            timestamp = round(idx / video_fps, 2)
            
            frame_name = f"frame_{saved_count:04d}.jpg"
            frame_path = os.path.join(out_dir, frame_name)

            cv2.imwrite(frame_path, frame)

            # Return the full object so next steps don't have to guess
            extracted_data.append({
                "path": frame_path,
                "timestamp": timestamp,
                "index": saved_count
            })
            
            saved_count += 1

        idx += 1

    cap.release()
    return extracted_data