import cv2


def comolokko():
    cap = cv2.VideoCapture(1)

    for i in range(91):
        _, frame = cap.read()
        cv2.imwrite(f"faces/image{i}.jpg", frame)


if __name__ == "__main__":
    comolokko()
