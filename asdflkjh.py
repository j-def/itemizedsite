import os
import glob
import re

my_dir = "./images/"
for fname in os.listdir(my_dir):
    print(fname)
    if fname.startswith("version"):
        os.remove(os.path.join(my_dir, fname))