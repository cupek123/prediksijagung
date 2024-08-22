from flask import Flask, request, render_template
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img , img_to_array

import os
import uuid
import flask
import urllib


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# model = load_model(os.path.join(BASE_DIR , 'model2.h5'))
# model = load_model(os.path.join(BASE_DIR , 'jagung.h5'))
# model = load_model(os.path.join(BASE_DIR , 'CNN_jagung.h5'))
model = load_model(os.path.join(BASE_DIR , 'jagung_CNN_30epoch.h5'))
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'jfif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


classes = ['Blight', 'Common_Rust', 'Gray_Leaf_Spot', 'Healthy']
def predict(filename, model):
    img = load_img(filename, target_size=(224, 224))
    img = img_to_array(img)
    img = img.reshape(1, 224, 224, 3)

    img = img.astype('float32')
    img = img / 255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(10):
        if i < len(result[0]):
            dict_result[result[0][i]] = classes[i]
        else:
            print(f"Indeks {i} di luar batas untuk hasil prediksi.")

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]

    prob_result = []
    class_result = []
    for i in range(3):
        if i < len(prob):
            prob_result.append((prob[i] * 100).round(2))
            class_result.append(dict_result[prob[i]])
        else:
            print(f"Indeks {i} di luar batas untuk probabilitas.")

    return class_result, prob_result


@app.route('/')
def home():
        return render_template("index.html")
@app.route('/success' , methods = ['GET' , 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd(), r'static\images')
    if request.method == 'POST':
        if(request.form):
            link = request.form.get('link')
            try :
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img , filename)
                output = open(img_path , "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result, prob_result = predict (img_path, model)

                predictions = {
                    "class1":class_result[0],
                    "class2":class_result[1],
                    "class3":class_result[2],

                    "prob1":prob_result[0],
                    "prob2":prob_result[1],
                    "prob3":prob_result[2],
                }
            except Exception as e : 
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'
            if(len(error) == 0):
                return render_template('success.html',img = img, predictions = predictions)
            else:
                return render_template('index.html', error = error) 
        
        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img , file.filename))
                img_path = os.path.join(target_img , file.filename)
                img = file.filename

                class_result , prob_result = predict(img_path, model)

                predictions = {
                    "class1":class_result[0],
                    "class2":class_result[1],
                    "class3":class_result[2],

                    "prob1":prob_result[0],
                    "prob2":prob_result[1],
                    "prob3":prob_result[2]
                }
            else:
                error = "Please upload image with format jgp, jpeg, png, and jfif only"
            if(len(error) == 0):
                return render_template('success.html',img = img, predictions = predictions)
            else:
                return render_template('index.html', error = error)
    else:
        return render_template ('index.html')


if __name__ == "__main__":
    app.run(debug=True)
