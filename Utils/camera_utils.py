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

    # Step 1 : Add Drawing Variables
    prev_x = None
    prev_y = None
    # prev_x, prev_y = 0, 0
    drawing_mode = False

    # Step 2 : Create Finger State Detector
    def fingers_up(hand):
        tips = [4, 8, 12, 16, 20]
        fingers = []

        # Thumb
        fingers.append(
            1 if hand.landmark[tips[0]].x >
                hand.landmark[tips[0] - 1].x else 0
        )

        # Other fingers
        for tip in tips[1:]:
            fingers.append(
                1 if hand.landmark[tip].y <
                    hand.landmark[tip - 2].y else 0
            )

        return fingers


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

                index_tip = handLms.landmark[8]

                cx = int(index_tip.x * w)
                cy = int(index_tip.y * h)

                cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

                # Draw whenever finger is visible
                if prev_x is not None:

                    # cv2.line(
                    #     img,
                    #     (prev_x, prev_y),
                    #     (cx, cy),
                    #     (255, 0, 255),
                    #     3
                    # )
                    cv2.circle(
                        img,
                        (cx, cy),
                        10,
                        (0, 255, 0),
                        cv2.FILLED
                    )

                    if actions and "draw" in actions:
                        try:
                            actions["draw"](
                                prev_x,
                                prev_y,
                                cx,
                                cy
                            )
                        except Exception as e:
                            print("DRAW ERROR:", e)

                prev_x = cx
                prev_y = cy
        else:
            prev_x, prev_y = None, None

        cv2.imshow("Camera", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if sound:
        sound.play("CameraClose")
