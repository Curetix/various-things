import time
import random
import pyautogui
import keyboard
from PIL import ImageGrab


def main():
    # wheel colors counter-clockwise (direction the wheel spins)
    wheel_color_sequence = (
        (239, 46, 19),  # red
        (0, 77, 242),  # blue
        (242, 218, 0),  # yellow
        (129, 158, 141),  # grey-ish
        (248, 142, 31),  # orange
        (133, 28, 197),  # purple
    )

    x = 640
    y_ball_start = 350
    y_ball_end = 820
    y_wheel = 830

    current_ball_color = None
    last_time = time.time()

    # Initial click to start game
    pyautogui.click()

    while True:
        if keyboard.is_pressed("x") or pyautogui.position().x > 1280:
            print("Stopping main loop.")
            break

        image = ImageGrab.grab()

        # Find ball between starting point and top of the wheel
        for y in range(y_ball_start, y_ball_end):
            pixel = image.getpixel((x, y))

            try:
                wheel_color_sequence.index(pixel)
            except ValueError:
                continue

            if pixel != current_ball_color:
                current_ball_color = pixel
                new_time = time.time()
                print("time since last ball: %s" % (new_time - last_time))
                last_time = new_time
                break

        current_wheel_color = image.getpixel((x, y_wheel))

        ball_color_index = wheel_color_sequence.index(current_ball_color)
        wheel_color_index = wheel_color_sequence.index(current_wheel_color)
        number_of_clicks = (ball_color_index - wheel_color_index) % len(wheel_color_sequence)

        if number_of_clicks == 0:
            continue

        print("Moving wheel from %s to %s with %s clicks" % (current_wheel_color, current_ball_color, number_of_clicks))

        for i in range(number_of_clicks):
            if keyboard.is_pressed("x"):
                break
            time.sleep(random.randint(47, 139) / 1000)
            pyautogui.click()


if __name__ == "__main__":
    print("Move mouse into position and press 's'. Hold 'x' to stop when running.")
    keyboard.wait("s")
    main()
