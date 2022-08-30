import os
import json
import urllib.request
from multiprocessing import cpu_count
from tqdm.contrib.concurrent import process_map

images_path = 'image/dress'
filename = 'metadata.json'

if not os.path.isdir(images_path):
    os.makedirs(images_path)


def download_metadata(url):
    if not os.path.exists(filename):
        urllib.request.urlretrieve(url, filename)


download_metadata('https://raw.githubusercontent.com/zalandoresearch/feidegger/master/data/FEIDEGGER_release_1.2.json')


def generate_image_list(filename):
    metadata = open(filename, 'r', encoding='utf-8')
    data = json.load(metadata)
    url_lst = []
    for i in range(len(data)):
        url_lst.append(data[i]['url'])
    return url_lst


def download_image(url):
    urllib.request.urlretrieve(url, images_path + '/' + url.split("/")[-1].split("?")[0])


# generate image list
url_lst = generate_image_list(filename)
workers = 2 * cpu_count()

if __name__ == '__main__':
    # downloading images to local disk
    process_map(download_image, url_lst, max_workers=workers)
