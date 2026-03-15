from __future__ import annotations

import threading
import time

import cv2


class GestureController:
    def __init__(
        self,
        on_fist,
        on_pinch,
        on_middle_pinch,
        on_error,
        camera_index: int,
        cooldown_seconds: float,
        show_camera_window: bool,
        hold_frames: int,
        release_frames: int,
        finger_margin: float,
        pinch_distance_threshold: float,
        pinch_hold_frames: int,
        pinch_cooldown_seconds: float,
    ) -> None:
        self.on_fist = on_fist
        self.on_pinch = on_pinch
        self.on_middle_pinch = on_middle_pinch
        self.on_error = on_error
        self.camera_index = camera_index
        self.cooldown_seconds = cooldown_seconds
        self.show_camera_window = show_camera_window
        self.hold_frames = hold_frames
        self.release_frames = release_frames
        self.finger_margin = finger_margin
        self.pinch_distance_threshold = pinch_distance_threshold
        self.pinch_hold_frames = pinch_hold_frames
        self.pinch_cooldown_seconds = pinch_cooldown_seconds

        self._running = False
        self._thread: threading.Thread | None = None
        self._last_trigger = 0.0
        self._closed_counter = 0
        self._open_counter = 0
        self._armed = True
        self._last_pinch_trigger = 0.0
        self._pinch_counter = 0
        self._pinch_open_counter = 0
        self._pinch_armed = True
        self._last_middle_pinch_trigger = 0.0
        self._middle_pinch_counter = 0
        self._middle_pinch_open_counter = 0
        self._middle_pinch_armed = True

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _is_fist_closed(self, lm) -> bool:
        tip_ids = [8, 12, 16, 20]
        pip_ids = [6, 10, 14, 18]
        return all(lm[tip].y > (lm[pip].y + self.finger_margin) for tip, pip in zip(tip_ids, pip_ids))

    def _thumb_index_distance(self, lm) -> float:
        thumb_tip = lm[4]
        index_tip = lm[8]
        dx = thumb_tip.x - index_tip.x
        dy = thumb_tip.y - index_tip.y
        return (dx * dx + dy * dy) ** 0.5

    def _thumb_middle_distance(self, lm) -> float:
        thumb_tip = lm[4]
        middle_tip = lm[12]
        dx = thumb_tip.x - middle_tip.x
        dy = thumb_tip.y - middle_tip.y
        return (dx * dx + dy * dy) ** 0.5

    def _loop(self) -> None:
        cap = None
        try:
            import mediapipe as mp

            if not hasattr(mp, "solutions"):
                version = getattr(mp, "__version__", "unknown")
                raise RuntimeError(
                    f"Incompatible mediapipe build detected ({version}): top-level 'solutions' is unavailable. "
                    "Install mediapipe==0.10.14 in the active interpreter with "
                    "'python -m pip install --force-reinstall mediapipe==0.10.14'."
                )

            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                raise RuntimeError("Could not open camera for gesture control.")

            mp_hands = mp.solutions.hands
            mp_draw = mp.solutions.drawing_utils

            with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.6, min_tracking_confidence=0.6) as hands:
                while self._running and cap.isOpened():
                    ok, frame = cap.read()
                    if not ok:
                        break

                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = hands.process(rgb)

                    if results.multi_hand_landmarks:
                        hand = results.multi_hand_landmarks[0]
                        lm = hand.landmark

                        is_closed = self._is_fist_closed(lm)
                        if is_closed:
                            self._closed_counter += 1
                            self._open_counter = 0
                        else:
                            self._open_counter += 1
                            self._closed_counter = 0
                            if self._open_counter >= self.release_frames:
                                self._armed = True

                        if (
                            self._armed
                            and self._closed_counter >= self.hold_frames
                            and (time.time() - self._last_trigger) > self.cooldown_seconds
                        ):
                            self.on_fist()
                            self._last_trigger = time.time()
                            self._armed = False

                        middle_pinch_now = self._thumb_middle_distance(lm) < self.pinch_distance_threshold
                        if middle_pinch_now:
                            self._middle_pinch_counter += 1
                            self._middle_pinch_open_counter = 0
                            self._pinch_counter = 0
                            self._pinch_open_counter = 0
                        else:
                            self._middle_pinch_open_counter += 1
                            self._middle_pinch_counter = 0
                            if self._middle_pinch_open_counter >= self.release_frames:
                                self._middle_pinch_armed = True

                        if (
                            self._middle_pinch_armed
                            and self._middle_pinch_counter >= self.pinch_hold_frames
                            and (time.time() - self._last_middle_pinch_trigger) > self.pinch_cooldown_seconds
                        ):
                            self.on_middle_pinch()
                            self._last_middle_pinch_trigger = time.time()
                            self._middle_pinch_armed = False

                        pinch_now = self._thumb_index_distance(lm) < self.pinch_distance_threshold
                        if pinch_now:
                            self._pinch_counter += 1
                            self._pinch_open_counter = 0
                        else:
                            self._pinch_open_counter += 1
                            self._pinch_counter = 0
                            if self._pinch_open_counter >= self.release_frames:
                                self._pinch_armed = True

                        if (
                            self._pinch_armed
                            and self._pinch_counter >= self.pinch_hold_frames
                            and (time.time() - self._last_pinch_trigger) > self.pinch_cooldown_seconds
                        ):
                            self.on_pinch()
                            self._last_pinch_trigger = time.time()
                            self._pinch_armed = False

                        if self.show_camera_window:
                            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                    if self.show_camera_window:
                        cv2.imshow("Gesture Control", frame)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            self._running = False
                            break
        except Exception as exc:
            self.on_error(str(exc))
        finally:
            if cap is not None:
                cap.release()
            cv2.destroyAllWindows()
            self._running = False
