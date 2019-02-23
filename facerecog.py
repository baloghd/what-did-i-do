import face_recognition
import glob
import pickle

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
images = [(x.split("/")[1].split("_"), face_recognition.load_image_file(x)) for x in image_paths]

if not model_ready:
	face_encodings = [(x[0], face_recognition.face_encodings(x[1])[0]) for x in images]
	with open("model", "wb") as model_pickle:
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
	return s