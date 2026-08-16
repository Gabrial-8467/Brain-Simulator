import os
import time
import threading
import cv2
import numpy as np
from .config import VISION_FPS, VISION_CAMERA_ID, FACES_DIR

class AashuEyes(threading.Thread):
    def __init__(self, brain_client, camera_id=VISION_CAMERA_ID, fps=VISION_FPS):
        super().__init__()
        self.client = brain_client
        self.camera_id = camera_id
        self.fps = fps
        self.running = False
        self.daemon = True
        self.last_face_crop = None
        self.last_frame = None
        self.scene_summary = None
        self.present_users = {}
        self.last_presence_event = None

        # Load OpenCV Haar Cascade face detector
        self.face_cascade = None
        try:
            if hasattr(cv2, 'CascadeClassifier'):
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
            else:
                print("Vision Info: CascadeClassifier not available in cv2. Face detection disabled.")
        except Exception as e:
            print(f"Vision Warning: Face detection classifier initialization failed ({e})")

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            print(f"Vision Alert: Could not open camera source {self.camera_id}")
            self.running = False
            return

        # Read initial frame for difference comparisons
        ret, prev_frame = cap.read()
        if not ret:
            cap.release()
            self.running = False
            return
        
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        
        delay = 1.0 / self.fps
        print("Camera Feed Started.")

        while self.running:
            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                break

            self.last_frame = frame

            # Convert to gray
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 1. Face Detection & Recognition
            face_count = 0
            recognized_user = None
            if self.face_cascade is not None:
                try:
                    faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
                    face_count = len(faces)
                    
                    if face_count > 0:
                        # Extract the first face
                        x, y, w, h = faces[0]
                        face_crop = gray[y:y+h, x:x+w]
                        self.last_face_crop = face_crop
                        
                        if os.path.exists(FACES_DIR):
                            face_std = cv2.resize(face_crop, (100, 100))
                            
                            # Compare against templates
                            best_score = 0.0
                            best_name = None
                            
                            for f in os.listdir(FACES_DIR):
                                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                                    tpl_path = os.path.join(FACES_DIR, f)
                                    tpl_img = cv2.imread(tpl_path, cv2.IMREAD_GRAYSCALE)
                                    if tpl_img is not None:
                                        tpl_std = cv2.resize(tpl_img, (100, 100))
                                        res = cv2.matchTemplate(face_std, tpl_std, cv2.TM_CCOEFF_NORMED)
                                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                                        if max_val > best_score:
                                            best_score = max_val
                                            best_name = os.path.splitext(f)[0]
                                            
                            # Threshold for template matching
                            if best_score > 0.65:
                                recognized_user = best_name
                except Exception:
                    pass

            # 2. Motion Detection (Frame Differencing)
            diff = cv2.absdiff(prev_gray, gray)
            _, diff_thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            motion_pixels = np.sum(diff_thresh == 255)
            total_pixels = gray.size
            motion_ratio = float(motion_pixels) / float(total_pixels)

            # 3. Average Brightness
            avg_brightness = float(np.mean(gray)) / 255.0

            # 4. Person presence tracking (stable across frames)
            now = time.time()
            if recognized_user:
                self.present_users[recognized_user] = now
            else:
                # Forget a user after a sustained absence
                for name in list(self.present_users.keys()):
                    if now - self.present_users[name] > 5.0:
                        del self.present_users[name]
            present = list(self.present_users.keys())

            # Fire a presence event the first time a known user is seen
            if recognized_user and (self.last_presence_event != recognized_user):
                self.last_presence_event = recognized_user
                threading.Thread(
                    target=self.client.send_perception_raw,
                    kwargs={
                        "payload": {
                            "content": f"The user {recognized_user} is now present in front of me",
                            "category": "user_presence",
                            "modality": "visual",
                            "valence": 0.2,
                            "intensity": 0.5,
                            "source": "eyes",
                        }
                    },
                    daemon=True
                ).start()

            # Store current frame as previous for next iteration
            prev_gray = gray.copy()

            # Compile sensory payload
            if face_count > 0 or motion_ratio > 0.05:
                objects = []
                attributes = {}
                relations = []
                confidence = 0.7

                if face_count > 0:
                    objects.append("face")
                    if recognized_user:
                        objects.append(recognized_user)
                        attributes["face"] = ["user", recognized_user]
                        confidence = 0.9
                    else:
                        attributes["face"] = ["unknown"]
                        confidence = 0.75
                elif present:
                    # A known user was recently present even if not in this exact frame
                    for name in present:
                        objects.append(name)
                        attributes["face"] = ["user", name]
                        confidence = 0.85

                if motion_ratio > 0.6:
                    relations.append({"from": "camera", "rel": "threat", "to": "environment"})

                if avg_brightness > 0.75:
                    attributes["camera"] = ["bright"]
                elif avg_brightness < 0.25:
                    attributes["camera"] = ["dark"]

                # Build a learning-worthy scene summary for the vision learning hook
                summary_parts = []
                if present:
                    summary_parts.append("the user " + " and ".join(present) + " present")
                elif recognized_user:
                    summary_parts.append(f"a face of the user {recognized_user}")
                elif "face" in objects:
                    summary_parts.append("an unknown face")
                if motion_ratio > 0.05:
                    summary_parts.append(f"notable motion (level {motion_ratio:.2f})")
                if "bright" in attributes.get("camera", []):
                    summary_parts.append("a bright environment")
                elif "dark" in attributes.get("camera", []):
                    summary_parts.append("a dark environment")
                if summary_parts:
                    self.scene_summary = "Seen in the environment: " + ", ".join(summary_parts) + "."

                # Non-blocking post to structured visual endpoint
                threading.Thread(
                    target=self.client.send_visual_signal,
                    kwargs={
                        "objects": objects,
                        "attributes": attributes,
                        "relations": relations,
                        "motion_level": float(motion_ratio),
                        "confidence": confidence,
                        "source": "camera_sensor"
                    },
                    daemon=True
                ).start()

            # Throttle to match target FPS
            elapsed = time.time() - start_time
            sleep_time = max(0.01, delay - elapsed)
            time.sleep(sleep_time)

        cap.release()
        print("Camera Feed Stopped.")

    def stop(self):
        self.running = False

    def recently_seen_users(self, within_seconds=30):
        """Names of recognized users seen recently (within the window)."""
        now = time.time()
        return [
            name
            for name, seen_at in self.present_users.items()
            if now - seen_at <= within_seconds
        ]

