import pandas as pd
import numpy as np
import urllib
import io
import cv2
import requests

search_url = "https://www3.arche.blue/mvp5/v1/1030/search"
fast_search_url = "https://www3.arche.blue/mvp5/v1/1030/fastSearch"
tweet_imgs = pd.read_csv('data/enriched_tweets1part.csv')

trained_files = [
    '0000004',
    '0000001',
    '0000006',
    '0000002',
    '0000008',
    '0000007',
    '0000000',
    '0000011',
    '0000009',
    '0000016',
    '0000012',
    '0000013',
    '0000017',
    '0000019',
    '0000020',
    '0000021',
    '0000025',
    '0000027',
    '0000028',
    '0000033',
    '0000035',
    '0000036',
    '0000037',
    '0000038',
    '0000040',
    '0000042',
    '0000043',
    '0000044',
    '0000048',
    '0000041',
    '0000049',
    '0000032',
]


def images_to_files(img_db, id_list, url_list):
    for i, (id, url) in enumerate(zip(id_list, url_list)):
        if pd.isnull(url):
            continue
        try:
            fname = 'img/{:07}.jpg'.format(i)
            fnameBW = 'img_bw/{:07}.jpg'.format(i)
            urllib.urlretrieve(url, fname)
            inImg = cv2.imread(fname, 0)
            cv2.imwrite(fnameBW, inImg)
            print '[OK] {}'.format(fname[:min(30,len(fnameBW))])
        except Exception,e:
            print 'get failed:[{}]'.format(fname[:min(30,len(fname))])
            print e.message
            continue
        img_db[i]=fname


def search_db( filename):
    file = open(filename, "rb")
    res = requests.post(search_url, files={'image': file})
    file.close()
    # Get Response
    result = []
    if res.status_code == 200:
        # res = json.dumps(res.json(), indent=4)
        for r in res.json():
          print r['id'],r['score']
          result.append((r['id'],r['score']))
    else:
        print '[FAIL]:{}',res.text[:min(30,len(res.text))]
        result = [[]]
    result = np.array(result)
    return result

def open_and_resize_image(filename):    # Read Image as Gray Scale
    inImg = cv2.imread(filename, 0)
    # Resize Image
    h, w = inImg.shape
    if w > 320 or h > 240:
        if float(w) / 320 > float(h) / 240:
            dw = 320
            dh = int(320.0 / w * h)
        else:
            dw = int(240.0 / h * w)
            dh = 240
        refImg = cv2.resize(inImg, (dw, dh), interpolation=cv2.INTER_AREA)
    else:
        refImg = inImg
    return refImg

def fast_search_db(filename):
    refImg = open_and_resize_image(filename)
    dh, dw = refImg.shape
    # Post Search Request
    mode = 0
    data = bytearray(
        [mode % 0x100, mode / 0x100, mode / 0x10000, mode / 0x1000000, 0, 0, 0, 0, dh % 0x100, dh / 0x100, dh / 0x10000,
         dh / 0x1000000, dw % 0x100, dw / 0x100, dw / 0x10000, dw / 0x1000000])
    for y in range(dh):
        data.extend(refImg[y])
    memfile = io.BytesIO()
    memfile.write(data)
    files = {"image": ("%s" % filename, memfile.getvalue(), "application/octet-stream")}
    res = requests.post(fast_search_url, files=files)
    # Get Response
    result = []
    if res.status_code == 200:
        # res = json.dumps(res.json(), indent=4)
        for r in res.json():
            print r['id'], r['score']
            result.append((r['id'], r['score']))
    else:
        print '[FAIL]:{}', res.text[:min(30,len(res.text))]
        print res.text
        result = [[]]

    if not len(result):
        return None

    result = np.array(result)
    tmpdf = pd.DataFrame(result, columns=['imgid', 'similarity'])
    tmpdf.sort_values(['similarity'], inplace=True)
    imgid = int(tmpdf.iloc[0]['imgid'])
    return int(trained_files[imgid])


def check_url(url):
    fname = 'tmp.jpg'
    urllib.urlretrieve(url, fname)
    print '[OK] {}'.format(url[:min(30, len(url))])
    match_index = fast_search_db(fname)
    matched_data = tweet_imgs.iloc[match_index]
    return matched_data


if __name__ == "__main__":
    print check_url("https://s.yimg.com/ny/api/res/1.2/sE1FEyPWXrCHdowaZ_C9wQ--/YXBwaWQ9aGlnaGxhbmRlcjtzbT0xO3c9ODAwO2g9NjAw/http://media.zenfs.com/en_us/News/afp.com/89e3c671959a6220b7089d4eeac5c029f0bfdc7f.jpg")


