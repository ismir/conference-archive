import os
import PIL
import pdf2image


HEIGHT = 150  # thumbnail height in pixel

# output path
path_thumbs = '../database/thumbnails/2017'
os.makedirs(path_thumbs, exist_ok=True)

path_pdf = '../database/pdfs/2017/ArigaFG17.pdf'
cur_fn = os.path.splitext(os.path.basename(path_pdf))[0]

# open pdf
try:
    images = pdf2image.convert_from_path(path_pdf)
except pdf2image.exceptions.PDFPageCountError:
    print('Could not open {}'.format(path_pdf))

for cur_idx, cur_img in enumerate(images):
    cur_ratio = cur_img.size[0] / cur_img.size[1]
    new_width = int(HEIGHT * cur_ratio)

    # resize and save
    out = cur_img.resize((new_width, HEIGHT), resample=PIL.Image.LANCZOS)
    path_out = os.path.join(path_thumbs, '{}_{}.png'.format(cur_fn, cur_idx))
    try:
        out.save(path_out)
    except IOError:
        print('Cannot save image: {}, {}'.format(cur_fn, cur_idx))
