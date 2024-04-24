import rembg
from PIL import Image

rembg.remove(Image.open('./nptest1.jpg')).save('./nptest1nobg.png')
