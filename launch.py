# -*- coding: utf-8 -*-

import numpy as np
import cv2
import nxt.brick
import nxt.error
import nxt.bluesock
import time
import os
import shutil
import subprocess
import re
import logging
from PIL import Image

print time.strftime('%H:%M:%S') + "  Start"
start_time = time.time()

##Bluetooth connection
sock = nxt.bluesock.BlueSock('00:16:53:13:42:5F').connect()
print time.strftime('%H:%M:%S') + "  Connected to nxt"

raw_input()

####
deltaXwill = 84
deltaYwill = 85
degreeBetweenXTileWill= 92
degreeBetweenYTileWill = -80
X0will = 123
Y0will = 120
MAILBOX = 0
path = 'C:\Users\stan\Desktop\Lund\LegoRobotRuzzle\Opencv_WebCa'
####

try:
    shutil.rmtree(path+'\\tmp')
except OSError:
    pass
os.mkdir(path+'\\tmp')

#We move out the phone
print time.strftime('%H:%M:%S') + "  Scrolling the phone out"
if sock:     
    sock.message_write (MAILBOX, "MOVEOUT")


#We take the picture
time.sleep(1)
print time.strftime('%H:%M:%S') + "  Taking picture"
os.system('SoftWare\snapz.exe')
os.system('convert  snapz.dib tmp\snapz.png')
os.system('convert tmp\snapz.png -rotate "180>" tmp\snapz.png')
os.system('del *.dib')
path1 = path + '\\Images\\'+time.strftime('%d%m%y_%H%M') + '.png'
path2 = path + '\\tmp\\snapz.png'
shutil.copy(path2, path1)

#We check for square
img = cv2.imread(path+'\\tmp\\snapz.png')
imgGr = cv2.imread(path+'\\tmp\\snapz.png',0)
ret,thresh =cv2.threshold(imgGr,150,255,cv2.THRESH_BINARY)
cv2.imwrite(path+'\\tmp\\threshold2.png', thresh)
img = cv2.imread(path+'\\tmp\\snapz.png')




#Convert image in HSV
hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

# define range of color in HSV
lower = np.array([0,0,150])
upper = np.array([255, 100,255])

# Create mask and find contour
mask = cv2.inRange(hsv, lower, upper)
cv2.imwrite(path+'\\tmp\\threshold.png', mask)
contours,h = cv2.findContours(mask,1,2)

## First we find the normal size of the white squares (width and height)
i = 0
j = 0
width = 0
height = 0
X0 = 0
Y0 = 0
for cnt in contours:
    rect = cv2.boundingRect(cnt)
    
    if rect[2] > 50 and rect[3] > 50 and rect[2] < 100 and rect[3] < 100:
        if width==0:
                width = rect[2]
        elif rect[2] < width:
                width = rect[2]
        if height==0:
                height = rect[3]
        elif rect[3] < height:
                height = rect[3]
        if X0==0:
            X0 = rect[0]+rect[2]
        elif rect[0]+rect[2] < X0:
            X0 = rect[0]+rect[2]
        if Y0==0:
            Y0 = rect[1]+rect[3]
        elif rect[1]+rect[3] < Y0:
            Y0 = rect[1]+rect[3]

X0 = X0-width
Y0 = Y0-height
print X0
print Y0

square = []

#We look for all the white square and check if some are not stick together
for cnt in contours:
    rect = cv2.boundingRect(cnt)  
    if rect[2] >= width and rect[3] >= height:    
        if rect[2]<2*width:
            square.append(rect)        
        else:
            rect1 = [rect[0],rect[1],width,rect[3]]
            rect2 = [rect[0]+width,rect[1],rect[2]-width,rect[3]]
            square.append(rect1)
            square.append(rect2)


if len(square) != 16:
    print time.strftime('%H:%M:%S') + "  Error : not enought squares detected : " + str(len(square))
else:
    print time.strftime('%H:%M:%S') + "  " + str(len(square)) + " squares detected"

#Then we can start letter detection
print time.strftime('%H:%M:%S') + "  Start to detect letters"
deltaX = 0 
deltaY = 0

for rect in square:
    crop =  thresh[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]
    cropHSV = hsv[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]
    cropBonus = img[rect[1]-7:rect[1]+13,rect[0]-7:rect[0]+13]
    cropBonusHSV = hsv[rect[1]-7:rect[1]+13,rect[0]-7:rect[0]+13]
    
    
    #We find where is the square on the screen (i and j are the position (i,j = {0,1,2,3})
    if rect[0]-X0<width:
        j = 0
    elif rect[0]-X0<2*width:
        j = 1
        deltaX = rect[0]+rect[2]-X0-width
    elif rect[0]-X0<3*width:
        j = 2
    else:
        j = 3

    if rect[1]-Y0<height:
        i = 0
    elif rect[1]-Y0<2*height:
        i = 1
        deltaY = rect[1]+rect[3]-Y0-height
    elif rect[1]-Y0<3*height:
        i = 2 
    else:
        i = 3

    
    #We look for bonus
    file_bonusB = path+'\\tmp\\'+str(i) +'x'+ str(j)+"_bonusB"+'.jpg'
    file_bonusG = path+'\\tmp\\'+str(i) +'x'+ str(j)+"_bonusG"+'.jpg'
    file_bonusY = path+'\\tmp\\'+str(i) +'x'+ str(j)+"_bonusY"+'.jpg'
    file_bonusR = path+'\\tmp\\'+str(i) +'x'+ str(j)+"_bonusR"+'.png'
    file_bonusE = path+'\\tmp\\'+str(i) +'x'+ str(j)+"_bonusE"+'.png'
    file_bonus = path+'\\tmp\\'+str(i) +'x'+ str(j)+"_bonus"+'.jpg'

    bonus = '_NN' 
    
    lowerR = np.array([0,100,80])
    upperR = np.array([20,255,255])
    lowerY = np.array([20,100,80])
    upperY = np.array([40,255,255])
    lowerG = np.array([40,100,80])
    upperG = np.array([60,255,255])
    lowerB = np.array([80,100,80])
    upperB = np.array([100,255,255])    
    lowerE = np.array([0,0,150])
    upperE = np.array([255,100,255])

    test = True
    maskE = cv2.inRange(cropBonusHSV, lowerE, upperE)
    cv2.imwrite(file_bonusE, maskE)
    cE,hE = cv2.findContours(maskE,1,2)
    nzE = np.count_nonzero(maskE)
    for cntE in cE:
        rectE = cv2.boundingRect(cntE)
        if nzE>100:
            test = False

    if test:
        bonus = '_TL'
        maskY = cv2.inRange(cropBonusHSV, lowerY, upperY)
        cv2.imwrite(file_bonusY, maskY)
        cY,hY = cv2.findContours(maskY,1,2)
        nzY = np.count_nonzero(maskY)
        for cntY in cY:
            rectY = cv2.boundingRect(cntY)
            if nzY>200:
                bonus = '_DW'
        
        maskR = cv2.inRange(cropBonusHSV, lowerR, upperR)
        cv2.imwrite(file_bonusR, maskR)
        cR,hR = cv2.findContours(maskR,1,2)
        nzR = np.count_nonzero(maskR)
        for cntR in cR:
            rectR = cv2.boundingRect(cntR)
            if nzR>200:
                bonus = '_TW'

        maskG = cv2.inRange(cropBonusHSV, lowerG, upperG)
        cv2.imwrite(file_bonusG, maskG)
        cG,hG = cv2.findContours(maskG,1,2)
        nzG = np.count_nonzero(maskG)
        for cntG in cG:
            rectG = cv2.boundingRect(cntG)
            if nzG>200:
                bonus = '_DL'

        maskB = cv2.inRange(cropBonusHSV, lowerB, upperB)
        cv2.imwrite(file_bonusB, maskB)     
        cB,hB = cv2.findContours(maskB,1,2)
        nzB = np.count_nonzero(maskB)
        
        for cntB in cB:
            rectB = cv2.boundingRect(cntB)
            if nzB>200:
                bonus = '_TL'

    cv2.imwrite(file_bonus, cropBonus)
    

    #Then we detect letter 
    file_letter = path+'\\tmp\\'+str(i) + str(j)+bonus+'.png'
    
    lower = np.array([0,0,150])
    upper = np.array([255,100,255])
    
    mask1 = cv2.inRange(cropHSV, lower, upper)
    c,h = cv2.findContours(mask1,1,2)

    for cnt1 in c:
        
        rect1 = cv2.boundingRect(cnt1)
        
        if rect1[3]>25 and rect1[3]<50 and rect1[2]>5 and rect1[2]<50 and rect1[1]>6:
            letter = crop[rect1[1]-12:rect1[1]+rect1[3]+5,rect1[0]-3:rect1[0]+rect1[2]+5]
            cv2.imwrite(file_letter,letter)

letter_pics = []
for files in os.listdir(path+'\\tmp\\'):
    if files.endswith(".png"):
        letter_pics.append(files) 


new_im = Image.new('RGBA', (592,52),(255,255,255,255))
referenceLetters = Image.open((path+"\\tmp\\firstthree.png")
new_im.paste(referenceLetters, (0,0))         
n = 0
for i in xrange(111,703,37):
    im = Image.open(path+"\\tmp\\"+letter_pics[n])
    new_im.paste(im, (i,0))
    n+=1
new_im.save(path+"\\tmp\\letters.png")
 
                
for cnt in contours:
    rect = cv2.boundingRect(cnt)  
    if rect[2] >= width and rect[3] >= height:    
        cv2.drawContours(img,[cnt],0,(0,255,0),-1)

cv2.imwrite(path+'\\tmp\\picture1.png', img)

#Tesseract
print time.strftime('%H:%M:%S') + "  Start Tesseract Detection"
try:
    os.remove('./bin/end.txt')
except OSError:
    pass
os.system(r'C:\cygwin\bin\bash --login -c "/cygdrive/c/Users/stan/Desktop/Lund/LegoRobotRuzzle/Opencv_WebCa/bin/tesseract.sh"')

while not os.path.isfile('./bin/end.txt'):
        time.sleep(1)
try:
    os.remove('./bin/end.txt')
except OSError:
    pass
print time.strftime('%H:%M:%S') + "  Tesseract is over"

#We move in the phone
print time.strftime('%H:%M:%S') + "  Scrolling the phone back"
if sock:     
    sock.message_write (MAILBOX, "MOVEIN")


#We send information to the NXT
print time.strftime('%H%M%S') + "  Sending information to the NXT"
degreeBetweenXTile= degreeBetweenXTileWill*deltaX/deltaXwill
degreeBetweenYTile= degreeBetweenYTileWill*deltaY/deltaYwill
offsetX = degreeBetweenXTileWill*(X0-X0will)/deltaXwill
offsetY = -1*degreeBetweenYTileWill*(Y0-Y0will)/deltaYwill
message = str(degreeBetweenXTile)+"*"+str(degreeBetweenYTile)+"*"+str(offsetX)+"*"+str(offsetY)+"*"
print message
print deltaX
print deltaY
if sock:
    sock.message_write(MAILBOX, message)


LETTERPOINTS = {
    'a': 1, 'b': 5, 'c': 8, 
    'd': 1, 'e': 1, 'f': 4, 
    'g': 3, 'h': 3, 'i': 1,
    'j': 7, 'k': 3, 'l': 2,
    'm': 3, 'n': 1, 'o': 2,
    'p': 4, 'q': 5, 'r': 1,
    's': 1, 't': 1, 'u': 4,
    'v': 3, 'w': 3, 'x': 8,
    'y': 10, 'z': 8, '0': 4,
    '1': 4, '2':4}


MIN_WORD_LENGTH = 4
MAX_WORD_LENGTH = 20


def getLettersFromRuzzle():
	print time.strftime('%H:%M:%S') + "  Start fetching letters from OCR"
	#subprocess.call("./readLetters.sh", shell=True)
	with open('./bin/output_sv.txt', 'r') as ocr:
		letters = ocr.readline()
	print time.strftime('%H:%M:%S') + "  Done fetching letters"
	letters = letters.replace(" ", "")
        letters = letters.replace("Ö", "2")
        letters = letters.replace("Ä", "1")
        letters = letters.replace("Å", "0")
	
	return letters

def getModifiersFromRuzzle():
	print time.strftime('%H:%M:%S') + "  Start fetching bonuses from OCR"
	with open('./bin/bonus.txt', 'r') as ocr:
		modifiers = ocr.readline()
	
	print "Done fetching letters"
	return list(modifiers)

def getWordsFromDictonary():
	print "Start fetching letters from dictionary"
	with open('./bin/dictionary_sv.txt', 'r') as dictionary:
		wordsFromDictionary = [line.rstrip() for line in dictionary]
	print time.strftime('%H:%M:%S') + "  Done fetching words"
	return wordsFromDictionary

def updateWordList(RUZZLE_STRING,wordsFromDictionary):
	letters = RUZZLE_STRING
	words = []
	tmp = []
	tmp.append('[')
	tmp.append(RUZZLE_STRING)
	tmp.append(']')
	regexpLetters = ''.join(tmp)
	for word in wordsFromDictionary:
		match = re.match(regexpLetters,word)
		if match is not None:
			words.append(word)	
	return words

def getWordParts(updatedWordList):
	wordParts = set()
	for line in updatedWordList:     
		wordPart = ""
		word = line
		for letter in word:
			wordPart += letter
			if(not wordPart in wordParts):
				wordParts.add(wordPart)
	return wordParts



def findWords(RUZZLE_STRING,RUZZLE_MODIFIERS,wordsFromDictionary):
	foundwords = []
	updatedWordList = updateWordList(RUZZLE_STRING,wordsFromDictionary)
	wordParts = getWordParts(updatedWordList)
	board = [[],[],[],[]]
	for i, L in enumerate(RUZZLE_STRING):
			board[i/4].append((L,RUZZLE_MODIFIERS[i],LETTERPOINTS[L],(i%4,i/4)))

			# recursive solver. 
			def solve(wurd,currentword, x, y):
				if (x > 3 or x < 0 or y > 3 or y < 0 or board[y][x] in currentword or len(currentword) > MAX_WORD_LENGTH):
					return
				V = currentword+[board[y][x],]
				W = wurd + board[y][x][0]
				if (len(V) >= MIN_WORD_LENGTH):
					if (W in updatedWordList):
						foundwords.append(V)
						logging.debug(",".join(map(lambda x: str(x[3]),V))+" - "+W+" - found"+'\n')
				if (W in wordParts):
					logging.debug(",".join(map(lambda x: str(x[3]),V))+" - "+W+" - parts"+'\n')
					solve(W,V,x+1,y+1)
					solve(W,V,x+1,y)
					solve(W,V,x+1,y-1)
					solve(W,V,x,y+1)
					solve(W,V,x,y-1)
					solve(W,V,x-1,y+1)
					solve(W,V,x-1,y)
					solve(W,V,x-1,y-1)
				else:
					logging.debug(",".join(map(lambda x: str(x[3]),V))+" - "+W+" - failed"+'\n')
	# initialize the solve functions on each starting location
	print(board)
	for x in range(4):
		for y in range(4):
			solve("",[],x,y)

	logging.info("scoring");
	wordlist = map(lambda word: ("".join(map(lambda v: v[0], word)),score(word),word ), foundwords)
	wordlist.sort(key=lambda word: word[1],reverse=True)
	checklist = set()
	for i, word in enumerate(wordlist):
		if word[0] in checklist:
			del(wordlist[i])
		else:
			checklist.add(word[0])


	#wordlist - all words, all points, all routes
	#wordlist[x] - one word with routes
	logging.debug(len(wordlist))
	logging.debug("wordlist[0]")
	logging.debug(wordlist[0])
	logging.debug("wordlist[0][0]") #Word
	logging.debug(wordlist[0][0])
	logging.debug("wordlist[0][1]") #Point
	logging.debug(wordlist[0][1])
	logging.debug("wordlist[0][2]") #Letters
	logging.debug(wordlist[0][2])
	logging.debug("wordlist[0][2][0]") #Letter
	logging.debug(wordlist[0][2][0])
	logging.debug("wordlist[0][2][0][3]") #Coordinate
	logging.debug(wordlist[0][2][0][3])
	logging.debug("wordlist[0][2][0][3][0]") #X
	logging.debug(wordlist[0][2][0][3][0])
	logging.debug("wordlist[0][2][0][3][1]") #Y
	logging.debug(wordlist[0][2][0][3][1])
	return wordlist
	
			

def score(word):
	letterModifiers = {
		't': 3,
		'd': 2,
		'n': 1,
                'T': 1,
		'D': 1
		}
	wordModifiers = {
		'T': 3,
		'D': 2,
		'n': 1,
		't': 1,
		'd': 1
		}
	wordMultiplier = 1
	letterScore = 0
	for letter in word:
                letterScore += letter[2] * (letterModifiers[letter[1]])
		wordMultiplier *= (wordModifiers[letter[1]])	
	return letterScore * wordMultiplier + max(len(word)-4,0) * 5
	

	

def createRoutes(words):
	coordinates = []
	routes = []

	for word in words:
	        logging.debug(map(lambda x: x[3],word[2]))
	        coordinates.append(map(lambda x: x[3],word[2]))

	for coordinate in coordinates:
		tmp = []
		for xy in coordinate:
			tmp.append(xy[0])
			tmp.append(xy[1])
		tmp.insert(2,4)
		tmp.append(5)
		tmp = ''.join(map(str,tmp))
		routes.append(tmp)	
	
	print(routes)

	return routes


def sendPath(path):
        MAILBOX = 0

        # Find the brick
        #sock = nxt.bluesock.BlueSock('00:16:53:13:42:5F').connect()
        
        if sock:
                #Start transmition
                sock.message_write (MAILBOX, "START")
                print time.strftime('%H:%M:%S') + "  Waiting for Clear To Send..."

                #Wait for clear to send
                message = ""
                while not ("CTS" in message):
                        try:
                                (inbox, message) = sock.message_read (10, 0, True)
                        except nxt.error.DirProtError, e:
                                time.sleep(0.1)
                        
                                
                print time.strftime('%H:%M:%S') + "  Clear To Send received"
                

                #Transmition
                print time.strftime('%H:%M:%S') + "  Sending route"
                l = len(path)
                while l>59:
                        path1 = path[0:58]
                        path = path.replace(path1, "",1)
                        sock.message_write (MAILBOX, path1)
                        l = len(path)  
			#time.sleep(0.1)
                sock.message_write (MAILBOX, path)

                #End of transmition
        	sock.message_write (MAILBOX, "END")
        	print time.strftime('%H:%M:%S') + "  End of transmition"
	
                #Wait for acknowledgement
                while True:
                        break
      

# Main code execution.
# First extracts letters with shellscript and puts all chars in a string
# Then opens the dictionary and returns a list over all words in dictionary
#
foundwords = []
logging.basicConfig(
			filename="ruzzlesolver.log",
		    filemode='a',
		    format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
		    datefmt='%H:%M:%S',
	        level=logging.INFO
	        )


RUZZLE_STRING = getLettersFromRuzzle().lower()
print(RUZZLE_STRING)
RUZZLE_MODIFIERS = getModifiersFromRuzzle()
print(RUZZLE_MODIFIERS)

DICTIONARY = getWordsFromDictonary()
 
FOUND_WORDS = findWords(RUZZLE_STRING, RUZZLE_MODIFIERS, DICTIONARY)
FOUND_ROUTES = createRoutes(FOUND_WORDS)
print len(FOUND_ROUTES)
path = ""
i=0
for word in FOUND_ROUTES:
        i+=1
        path = path + word
        if i == 150:
                break
print time.strftime('%H:%M:%S') + "  End"
print time.time() - start_time, "seconds"

sendPath(path)

