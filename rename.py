import os
import glob

files = glob.glob("dataset/*")
stripped = [f.split("_")[0][8:] + ".jpg" for f in files]

from_to = list(zip(files, stripped))                              

for file in from_to:
	os.rename(file[0], file[1])