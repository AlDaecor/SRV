#Libraries
import cv2
import numpy as np
import os
import imutils
from imutils import contours
from imutils.perspective import four_point_transform
import pytesseract
from pytesseract import Output
from datetime import datetime

# Establishes the PATH for tesseract so it can work properly
pytesseract.pytesseract.tesseract_cmd = 'c:/Program Files/Tesseract-OCR/tesseract.exe'

# **********************************************************************************************************************
# Functions
def takePicture():
    """Captures a video of about 4 seconds to clean and load the image properly"""
    cap = cv2.VideoCapture(0)

    for i in range(0, 29):
        ret, image = cap.read()
        if ret == True:
            cv2.imshow('video', image)
            cv2.waitKey(1)
            cv2.destroyAllWindows()
    
    cap.release()

    return image
    

def ImageCrop(template):
    """in charge of cleaning and cropping the input image properly and returns an output ready for work"""
    Ref = cv2.imread('refs/ref1.png')
    gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(gray, 50, 150, 255)
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    displayCnt = None

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            displayCnt = approx
            break
    
    output = four_point_transform(template, displayCnt.reshape(4, 2))
    refw, refh, ref_ = Ref.shape
    outputw, outputh, output_ = output.shape

    #if para considerar si la template (la imagen que tomo la camara) es mas grande que la de referencia
    output = cv2.resize(output, (0,0), fx=(refw/outputw), fy=(refh/outputh))

    return output


def PatternId (list,image):
    """In charge of recognizing the patterns the user is looking for"""
    for pattern in list:
        icon = cv2.imread('icons/{}.png'.format(pattern))
        w,h,_ = icon.shape

        res = cv2.matchTemplate(icon, image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        bottom_right = (max_loc[0] + w, max_loc[1] + h)
        cv2.rectangle(image, max_loc, bottom_right, 255, 2)

        percentage = max_val*100
        percentage = str(round(percentage, 2))
        if max_val >= .60:
            print('{} has been identified with a {}%'.format(pattern, percentage), 'of accuracy')
        else:
            print("{} wasn't identified in the image".format(pattern))
    
    return image


def WordId (list, image):
    """In charge of recognizing the words the user is looking for"""
    
    for word in list:
        nonResponse = image.copy()
        turn = 0
        wordflag = []
        d = pytesseract.image_to_data(image, output_type=Output.DICT)
        n_boxes = len(d['level'])

        while turn <= 4:
            turn += 1
            for i in range(n_boxes):
                text = d['text'][i]
                if text == word:
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    wordflag.append((x,y,w,h))
                    #print(wordflag)
                    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), -1)

            if len(wordflag) == 0:
                image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

            elif len(wordflag) == 1:
                turnsleft = 5 - turn
                while turnsleft > 0:
                    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                    turnsleft -= 1

                turn = 5
        
        if len(wordflag) == 0:
            print('the word: "{}" was not found, please be sure to type it as it should appear'.format(word))
            image = nonResponse
        
        #if wordflag == 0:
        #    image = nonResponse

    return image


#*****************************************************************************************************************************
# Main code
while True:
    # Receive the command from the user
    useri = input('>')

    # Clean and divide the input into segments and turn the whole input into lowercase letters
    useri = str(useri).lower()
    userlist = useri.split(' ')

    # Config mode - to set certain parameters that aren't included in other sections
    if userlist[0] == 'config':
        print('Now in "config" mode')
        print('Adjusting light level to {}%'.format(userlist[1]))

    # Look mode - to look for colors, patterns or words. either all at once or just certain options
    elif userlist[0] == 'look':
        # Entered look mode, which will look for colors and patterns
        print('Now in "look" mode')

        # Might move this 2 next lines into the function
        #imgTemplate = cv2.imread('templates/template{}.jpg'.format(userlist[1]))
        imgTemplate = cv2.imread('templates/templateIRL.png')
        output = ImageCrop(imgTemplate)
        iconoutput = output.copy()
        wordoutput = output.copy()

        if userlist[2] != 'false':
            if userlist[2] == 'true':
                userwordi = input('Type the key words separated by commas and without spaces unless needed so:\n> ')
                keywords = userwordi.split(',')
                wordoutput = WordId(keywords, wordoutput)
            else:
                print('only "true" or "false" can go into the keywords parameter')
        
        if userlist[1] != 'null': # Fourth element in the vector corresponds to the icons the user wants to find
            
            userlist_Icons = userlist[1].split(',')
            cleanlist_Icons = []
            dir_path = 'icons/'
            counter = 0

            if '*' in userlist[1]:
                print('todos')
                for path in os.listdir(dir_path):
                    if os.path.isfile(os.path.join(dir_path, path)):
                        counter += 1    

            elif userlist[1] != '*':
                for icon in userlist_Icons:
                    if '{}.png'.format(icon) not in os.listdir(dir_path):
                        print('"{}" not present in the available icons\nignoring input.'.format(icon))
                    if '{}.png'.format(icon) in os.listdir(dir_path):
                        print('icon accepted...')
                        cleanlist_Icons.append(icon)
                
                iconoutput=PatternId(cleanlist_Icons,iconoutput)
                #cv2.imshow('icon output', iconoutput)
                #cv2.waitKey()
    

        # we obtain all the results the user is looking for and we add them all into a single image, ready to be logged
        alpha = 0.4
        output = cv2.addWeighted(wordoutput, alpha, output, 1 - alpha, 0)
        output = cv2.addWeighted(iconoutput, alpha, output, 1 - alpha, 0)

        now = datetime.now()
        dt_string = now.strftime('%d_%m_%Y %H_%M_%S')
        cv2.imwrite("logs/{}_{}.jpeg".format(userlist[3], dt_string),output)

    # Exit command
    elif userlist[0] == 'exit':
        exit()
    
    # In case no available command was used
    else:
        print('Setting mode not identified, type "help" if you wish to see the available settings modes')