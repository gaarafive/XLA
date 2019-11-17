# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import re
import io
import json
import ftfy
# from nostril import nonsense
VIETNAMESE_DIACRITIC_CHARACTERS = "ẮẰẲẴẶĂẤẦẨẪẬÂÁÀÃẢẠĐẾỀỂỄỆÊÉÈẺẼẸÍÌỈĨỊỐỒỔỖỘÔỚỜỞỠỢƠÓÒÕỎỌỨỪỬỮỰƯÚÙỦŨỤÝỲỶỸỴ"
VIETNAMESE_DIACRITIC_CHARACTERS += VIETNAMESE_DIACRITIC_CHARACTERS.lower()
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
                help="type of preprocessing to be done, choose from blur, linear, cubic or bilateral")
args = vars(ap.parse_args())

image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

if args["preprocess"] == "thresh":
    gray = cv2.threshold(gray, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

elif args["preprocess"] == "adaptive":
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

if args["preprocess"] == "linear":
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

elif args["preprocess"] == "cubic":
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)




if args["preprocess"] == "blur":
    gray = cv2.medianBlur(gray, 3)

elif args["preprocess"] == "bilateral":
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

elif args["preprocess"] == "gauss":
    gray = cv2.GaussianBlur(gray, (5,5), 0)

filename = "{}.png".format(os.getpid())
cv2.imwrite(filename, gray)

text = pytesseract.image_to_string(Image.open(filename), lang = 'vie')
os.remove(filename)
text_output = open('outputbase.txt', 'w', encoding='utf-8')
text_output.write(text)
text_output.close()

file = open('outputbase.txt', 'r', encoding='utf-8')
text = file.read()
# print(text)

# Cleaning all the gibberish text
text = ftfy.fix_text(text)
text = ftfy.fix_encoding(text)
'''for god_damn in text:
    if nonsense(god_damn):
        text.remove(god_damn)
    else:
        print(text)'''
idcard = None
name = None
dob = None
pan = None
sex = None
nationality = None
homeland = None
placeofresidence = None

nameline = []
dobline = []
panline = []
text0 = []
text1 = []
text2 = []

# Searching for PAN
lines = text.split('\n')
for lin in lines:
    s = lin.strip()
    s = lin.replace('\n','')
    s = s.rstrip()
    s = s.lstrip()
    text1.append(s)

text1 = list(filter(None, text1))
# print(text1)

lineno = 0

for wordline in text1:
    xx = wordline.split('\n')
    if ([w for w in xx if re.search('(INCOMETAXDEPARWENT @|mcommx|INCOME|TAX|GOW|GOVT|GOVERNMENT|OVERNMENT|VERNMENT|DEPARTMENT|EPARTMENT|PARTMENT|ARTMENT|INDIA|NDIA)$', w)]):
        text1 = list(text1)
        lineno = text1.index(wordline)
        break

# text1 = list(text1)
text0 = text1[lineno+1:]
print(text0)

def findword(textlist, wordstring):
    lineno = -1
    for wordline in textlist:
        xx = wordline.split( )
        if ([w for w in xx if re.search(wordstring, w)]):
            lineno = textlist.index(wordline)
            textlist = textlist[lineno+1:]
            return textlist
    return textlist

try:

    name = text0[3]
    name = re.sub('[0-9a-zA-Z\s'+VIETNAMESE_DIACRITIC_CHARACTERS+']*:', '', name)
    name = re.sub('[0-9a-zA-Z\s'+VIETNAMESE_DIACRITIC_CHARACTERS+']*tên', '', name)
    name = name.rstrip()
    name = name.lstrip()
    dob = text0[4]
    dob = dob.replace(',', '')
    dob = dob.replace(':', '')
    dob = dob.replace('\"', '/1')
    dob = re.sub("[a-zA-Z"+VIETNAMESE_DIACRITIC_CHARACTERS +"]", "", dob)
    dob = dob.rstrip()
    dob = dob.lstrip()
    pan = text0[2]
    pan = pan.replace(" ", "")
    pan = pan.replace("\"", "")
    pan = pan.replace(";", "")
    pan = pan.replace("%", "L")
    pan = re.sub("[a-zA-Z\s"+VIETNAMESE_DIACRITIC_CHARACTERS +"]", '', pan)
    pan = pan.rstrip()
    pan = pan.lstrip()

    homeland = text0[6]
    homeland = re.sub("[a-zA-Z\s"+VIETNAMESE_DIACRITIC_CHARACTERS +"]*\:", '', homeland)
    homeland = homeland.rstrip()
    homeland = homeland.lstrip()

    placeofresidence = text0[7]
    placeofresidence = re.sub("[a-zA-Z\s"+VIETNAMESE_DIACRITIC_CHARACTERS +"]*\:", '', placeofresidence)
    placeofresidence = placeofresidence.rstrip()
    placeofresidence = placeofresidence.lstrip()
    placeofresidence += ", " + text0[8]
except:
    pass

data = {}
data['Name'] = name
data['Date of Birth'] = dob
data['Id Card'] = pan
data['Home Land'] = homeland
data['Place of Fresidence'] = placeofresidence


try:
    to_unicode = unicode
except NameError:
    to_unicode = str

# Write JSON file
with io.open('data.json', 'w', encoding='utf-8') as outfile:
    str_ = json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(str_))

# Read JSON file
with open('data.json', encoding = 'utf-8') as data_file:
    data_loaded = json.load(data_file)

with open('data.json', 'r', encoding= 'utf-8') as f:
    ndata = json.load(f)



print('\t', "|++++++++++++++++++++++++++++++++++++++++++++++++++++++++|")
print('\t', '', '\t', ndata['Id Card'])
print('\t', "|--------------------------------------------------------|")
print('\t', '', '\t', ndata['Name'])
print('\t', "|--------------------------------------------------------|")
print('\t', '', '\t', ndata['Date of Birth'])
print('\t', "|--------------------------------------------------------|")
print('\t', '', '\t', ndata['Home Land'])
print('\t', "|--------------------------------------------------------|")
print('\t', '', '\t', ndata['Place of Fresidence'])
print('\t', "|++++++++++++++++++++++++++++++++++++++++++++++++++++++++|")
