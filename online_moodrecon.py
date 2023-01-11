from fer import FER
import matplotlib.pyplot as plt

test_image_one = plt.imread("user_photo_510495289.jpg")
emo_detector = FER(mtcnn=True)

captured_emotions = emo_detector.detect_emotions(test_image_one)
print(captured_emotions)

