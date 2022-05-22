import os
import cv2
import numpy as np
import tensorflow as tf
import pytesseract as pt

pt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
model_path = "static/models/full_model"


def get_model(model_path):
    loaded = tf.saved_model.load(model_path)
    infer = loaded.signatures["serving_default"]
    return infer


model = get_model(model_path)

def object_detection(path, filename):
    # read image
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_arr_224 = cv2.resize(image, (224, 224)) / 255.0

    h, w, d = image.shape
    test_arr = image_arr_224.reshape(1, 224, 224, 3)
    test_arr = tf.constant(test_arr, dtype=tf.float32)
    # make predictions
    coords = model(test_arr)['dense_2'].numpy()
    # denormalize the values
    denorm = np.array([w, h, w, h])
    coords = coords * denorm
    coords = coords.astype(np.int32)
    # draw bounding on top the image
    xmin, ymin, xmax, ymax = coords[0]
    # Enlarge the box for better OCR
    f = 0.02
    xmin = int(xmin - f * w)
    xmax = int(xmax + f * w)
    ymin = int(ymin - f * h)
    ymax = int(ymax + f * h)
    pt1 = (xmin, ymin)
    pt2 = (xmax, ymax)
    print(pt1, pt2)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.rectangle(image, pt1, pt2, (0, 255, 0), 3)
    cv2.imwrite('./static/predict/{}'.format(filename), image)
    coords = np.array([xmin, ymin, xmax, ymax])
    return coords


def save_text(filename, text):
    name, ext = os.path.splitext(filename)
    with open('./static/predict/{}.txt'.format(name), mode='w') as f:
        f.write(text)
    f.close()

def process_text(text):
    letters=[]
    for i,l in enumerate(text):
        if l.isupper() or l.isdigit() or l==" ":
            letters.append(l)

    if letters[-1]==" ":
        letters.pop(-1)
    if letters[0]==" ":
        letters.pop(0)
    ptext = "".join(letters)

    return ptext

def OCR(path, filename):
    img = cv2.imread(path)
    cods = object_detection(path, filename)
    xmin, ymin, xmax, ymax = cods
    roi_bgr = img[ymin:ymax, xmin:xmax]
    gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    magic_color = apply_brightness_contrast(gray, brightness=40, contrast=70)
    cv2.imwrite('./static/roi/{}'.format(filename), roi_bgr)

    text = pt.image_to_string(magic_color, lang='eng', config='--psm 6')
    try:
        text = process_text(text)
    except:
        pass
    print(text)
    save_text(filename, text)
    return text


def apply_brightness_contrast(input_img, brightness=0, contrast=0):
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow

        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)

        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf
