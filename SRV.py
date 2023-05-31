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


def ColorId (list,image):
    """In charge of recognizing the colors the user is looking for"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    if 'cyan' in list: 
        thresh = cv2.inRange(hsv, np.array([60, 50, 50], np.uint8), np.array([155, 250, 250], np.uint8))
        #cyan_range = [(np.array([60, 50, 50], np.uint8)),       # Cyan lower limit
        #                (np.array([155, 255, 255], np.uint8))]  # Cyan upper limit
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) > 0:
            print('Color cyan was found...')
            for c in cnts:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        else:
            print("Color cyan wasn't found... ")
 
    if 'red' in list:
        thresh = cv2.inRange(hsv, np.array([160, 50, 50], np.uint8), np.array([180, 250, 250], np.uint8))
        #red_range = [(np.array([160, 50, 50], np.uint8)),       # Red lower limit
        #                (np.array([180, 255, 255], np.uint8))]  # Red upper limit
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) > 0:
            print('Color red was found...')
            for c in cnts:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        else:
            print("Color red wasn't found..." )

    if 'orange' in list:
        thresh = cv2.inRange(hsv, np.array([5, 50, 50], np.uint8), np.array([15, 250, 250], np.uint8))
        #orange_range = [(np.array([5, 50, 50], np.uint8)),      # Orange lower limit
        #                (np.array([15, 255, 255], np.uint8))]   # Orange upper limit
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) > 0:
            print('Color orange was found...')
            for c in cnts:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            print("Color orange wasn't found...")
    
    return image


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
        
    if wordflag == 0:
        print()

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
        imgTemplate = cv2.imread('templates/template{}.jpg'.format(userlist[1]))
        
        output = ImageCrop(imgTemplate)
        iconoutput = output.copy()
        wordoutput = output.copy()

        if userlist[4] != 'false':
            if userlist[4] == 'true':
                userwordi = input('Type the key words separated by commas and without spaces unless needed so:\n> ')
                keywords = userwordi.split(',')
                wordoutput = WordId(keywords, wordoutput)
            else:
                print('only "true" or "false" can go into the keywords parameter')

        if userlist[2] != 'null': # the third element in the vector corresponds to the color the user is looking for

            userlist_Colors = userlist[2].split(',') # split the first command item into a vector depending on the user input

            if '*' in userlist_Colors:
                userlist_Colors = ['red', 'orange', 'cyan']
                
            if 'red' not in userlist_Colors and 'orange' not in userlist_Colors and 'cyan' not in userlist_Colors:
                print('Color not available, please try again with one of the available colors (Red, Orange, Cyan)')

            coloroutput = ColorId(userlist_Colors, output)
        
        if userlist[3] != 'null': # Fourth element in the vector corresponds to the icons the user wants to find
            
            userlist_Icons = userlist[3].split(',')
            cleanlist_Icons = []
            dir_path = 'icons/'
            counter = 0

            if '*' in userlist[3]:
                print('todos')
                for path in os.listdir(dir_path):
                    if os.path.isfile(os.path.join(dir_path, path)):
                        counter += 1    

            elif userlist[3] != '*':
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
        output = cv2.addWeighted(coloroutput, alpha, output, 1 - alpha, 0)
        output = cv2.addWeighted(iconoutput, alpha, output, 1 - alpha, 0)

        now = datetime.now()
        dt_string = now.strftime('%d_%m_%Y %H_%M_%S')
        cv2.imwrite("logs/{}_{}.jpeg".format(userlist[5], dt_string),output)

    # Exit command
    elif userlist[0] == 'exit':
        exit()
    
    # In case no available command was used
    else:
        print('Setting mode not identified, type "help" if you wish to see the available settings modes')