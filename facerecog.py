import face_recognition
import glob
import pickle
from PIL import Image, ImageTk  

import tkinter as tk  

from jinja2 import Template, Environment, PackageLoader, select_autoescape, FileSystemLoader

model_ready = False
try:
	with open("model", "rb") as model:
		model_pickle = pickle.load(model)
		model_ready = True
		print("model loaded")
except:
	print("model not loaded, training model")
	pass

image_paths = glob.glob("dataset/*")
images = []

for x in image_paths:
	try:
		images.append([x.split("/")[1].split("_"), face_recognition.load_image_file(x)])
	except:
		pass

if not model_ready:
	#face_encodings = [(x[0], face_recognition.face_encodings(x[1])[0]) for x in images]
	
	face_encodings = []
	for x in images:
		try:
			face_encodings.append([x[0], face_recognition.face_encodings(x[1])[0]])
		except:
			pass

	with open("model", "wb") as model_pickle:
		print(f"model pickled with {len(face_encodings)} faces")
		pickle.dump(face_encodings, model_pickle)
else:
	face_encodings = model_pickle


def get_similars(filename: str):
	image_to_test = face_recognition.load_image_file(filename)
	image_to_test_encoding = face_recognition.face_encodings(image_to_test)[0]
	known_encodings = [x[1] for x in face_encodings]
	face_distances = face_recognition.face_distance(known_encodings, image_to_test_encoding)
	#for i, distance in enumerate(face_distances):
	#	print("The test image has a distance of {:.2} from known image #{} ({})".format(distance, i, face_encodings[i][0]))
	s = sorted(list(zip([f[0] for f in face_encodings], face_distances)), key = lambda x: x[1])
	print(s[:10])
	top_n_similar_files = lambda n: ["dataset/" + "_".join(image[0]) for image in s[:n]] 
	return s, top_n_similar_files(4)

def show_similars(fn: str):
	sims = get_similars(fn)
	testimg = Image.open(fn)
	#testimg.show()

	root = tk.Tk()  
	root.title("display image")  
	photo=ImageTk.PhotoImage(testimg).zoom(0.6, 0.6)
	cv = tk.Canvas()  
	cv.pack(side='top', fill='both', expand='yes') 
	cv.create_image(10, 10, image=photo, anchor='nw') 
	i = 10
	#for img in sims[1]:
	#	print(img)
	p = [ImageTk.PhotoImage(Image.open(img)) for img in sims[1]]

	cv.create_image(i+450, 10, image=p[0], anchor='nw') 
	cv.create_image(i+800, 10, image=p[1], anchor='nw') 
	cv.create_image(i+1150, 10, image=p[2], anchor='nw') 
	root.geometry("1600x800")
	root.mainloop()

def html_similars(fn: str):
	env = Environment(
    autoescape=select_autoescape(['html'])
	)

	loader = FileSystemLoader('./')
	t = Template(loader.get_source(env, template = 'html/index.html')[0])

	sims = get_similars(fn)[1]
	filenames = [" ".join(s.split("/")[-1].split("_")[:-1]) for s in sims]
	t.stream(teszt = fn, hasonlok = list(zip(sims, filenames))).dump("html/" + fn.split("/")[-1] + ".html")

tesztek = glob.glob("tests/*")
for teszt in tesztek:
	print("generating " + teszt)
	html_similars(teszt)