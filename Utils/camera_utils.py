import cv2
import mediapipe as mp
import time


def start_camera(sound=None, actions=None):

    if sound:
        sound.play("CameraOpen")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=1)
    mpDraw = mp.solutions.drawing_utils

    prev_time = 0

    # Define button areas (x1,y1,x2,y2)
    buttons = {
        "save": (20, 20, 140, 80),
        "clear": (160, 20, 280, 80),
        "mute": (300, 20, 420, 80),
        "text": (440, 20, 560, 80),
    }

    trigger_cooldown = 0

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        h, w, _ = img.shape

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        # Draw buttons
        for name, (x1, y1, x2, y2) in buttons.items():
            cv2.rectangle(img, (x1, y1), (x2, y2), (50, 50, 50), -1)
            cv2.putText(img, name.upper(), (x1 + 10, y1 + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:

                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

                # Get index finger tip
                index_tip = handLms.landmark[8]
                cx, cy = int(index_tip.x * w), int(index_tip.y * h)

                cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

                # Button detection
                for name, (x1, y1, x2, y2) in buttons.items():
                    if x1 < cx < x2 and y1 < cy < y2:

                        if time.time() - trigger_cooldown > 1:
                            trigger_cooldown = time.time()

                            if actions and name in actions:
                                actions[name]()  # Trigger main app action

        curr_time = time.time()
        fps = int(1 / (curr_time - prev_time)) if prev_time else 0
        prev_time = curr_time

        # cv2.putText(img, f"FPS: {fps}", (10, 120),
        #             cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

        cv2.imshow("Camera", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if sound:
        sound.play("CameraClose")
