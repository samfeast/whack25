import cv2
from deepface import DeepFace
import threading
from operator import itemgetter

import queue
import sounddevice as sd
import vosk
import json

prev_dom = ""

emotion_list = ["", "", "", "", "", ""]

def enew(new_emotion):
    emotion_list[4] = emotion_list[3]
    emotion_list[3] = emotion_list[2]
    emotion_list[2] = emotion_list[1]
    emotion_list[1] = emotion_list[0]
    emotion_list[0] = new_emotion


def voice():
    model_path = "vosk-model-en-us-0.22"
    words = ""

    try:
        model = vosk.Model(model_path)
    except Exception as e:
        print(f"Error loading Vosk model at '{model_path}': {e}")
        print("Vosk thread terminated.")
        return

    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time, status):
        audio_queue.put(bytes(indata))

    sample_rate = 16000

    dindex = None
    try:
        dindex = sd.default.device[0]
        device_info = sd.query_devices(dindex)
        if device_info['max_input_channels'] == 0:
             dindex = None
    except Exception:
        dindex = None
            
    if dindex is None:
        print("Error: Could not find or access a microphone input device.")
        return

    try:
        with sd.RawInputStream(device=dindex, channels=1, samplerate=sample_rate, blocksize=8000, dtype='int16',
                               callback=audio_callback):
            print("Vosk: Listening... (Voice thread started)")
            recognizer = vosk.KaldiRecognizer(model, sample_rate)

            while True:
                data = audio_queue.get() 

                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    result_dict = json.loads(result)
                    rec_text = result_dict.get('text', '')
                    emotion_list[5] = str(rec_text)
                    try:
                        with open('../frontend/my-app/src/fer.txt', 'w') as file:
                            for i in emotion_list:
                                file.write( str(i) + "\n")
                    except Exception as e:
                        print(e)

                #else:
                #    partial_result = recognizer.PartialResult()
                #    partial_result_dict = json.loads(partial_result)

    except Exception as e:
        print(f"Vosk Thread Error: {e}")


voice_thread = threading.Thread(target=voice, daemon=True)
voice_thread.start()
print("Voice recognition thread started.")

FRAME_SKIP = 1
frame_count = 0

current_frame = None
latest_results = None
analysis_lock = threading.Lock()

print("Starting real-time Facial Expression Recognition...")

def analyze_worker():
    global latest_results, current_frame

    while True:
        frame_to_analyze = current_frame 
        
        if frame_to_analyze is not None:
            try:
                results = DeepFace.analyze(
                    img_path=frame_to_analyze,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='opencv' 
                )
                
                with analysis_lock:
                    latest_results = results
                    
            except Exception as e:
                with analysis_lock:
                    latest_results = None 

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) 
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

analysis_thread = threading.Thread(target=analyze_worker, daemon=True)
analysis_thread.start()

print("Analysis worker thread started. Press 'q' to exit.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    frame_count += 1
    if frame_count % FRAME_SKIP == 0:
        current_frame = frame.copy() 
        frame_count = 0

    with analysis_lock:
        results_to_draw = latest_results
        
    if results_to_draw:
        for result in results_to_draw:
            dominant_emotion = result['dominant_emotion'].upper()

            if result['face_confidence'] > 0.49 and result['dominant_emotion'] != prev_dom:
                es = result['emotion']

                emotion_scores_list1 = [
                    ["angry", es['angry']],
                    ["disgust", es['disgust']],
                    ["fear", es['fear']],
                    ["happy", es['happy']],
                    ["sad", es['sad']],
                    ["suprise", es['surprise']],
                    ["neutral", es['neutral']]
                ]

                emotion_string = ""

                emotion_scores_list = sorted(emotion_scores_list1, key=itemgetter(1))

                for i in emotion_scores_list:
                    if i[1] > 10:
                        emotion_string += str(i[0] + "(" + str(int(i[1])) + "%) " )

                enew(emotion_string)

                try:
                    with open('../frontend/my-app/src/fer.txt', 'w') as file:
                        for i in emotion_list:
                            file.write( str(i) + "\n")
                except Exception as e:
                    print(e)

                prev_dom = result['dominant_emotion']
            
            region = result['region']
            x, y, w, h = region['x'], region['y'], region['w'], region['h']
            
            color = (0, 255, 0)
            if dominant_emotion in ['ANGRY', 'FEAR', 'SAD']:
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            text = f"Emotion: {dominant_emotion}"
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.9, color, 2, cv2.LINE_AA)

    cv2.imshow('Real-time Facial Expression Recognition (Stable)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Webcam closed and program terminated.")