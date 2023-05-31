# SRV
 Sistema de Reconocimiento Visual para el termostato

# INSTALLATION

Before starting, the user must check if the next list of libraries are installed in the device:

-Cv2
-Numpy
-Os
-Imutils
-Pytesseract

For Pytesseract, it is highly suggested to use the installer that comes with the code, this is because the installer automatically configures the proper PATH
that is used for and in this code.


# CODE DESCRIPTION

The code is in the last stages, it can detect colors, icons and words:

Colors are limited to:
Orange, cyan and Red

For icons: 
please refer to the 'Icons' directory for all the available options

For words:
As long as they are typed the exact same way they appear in the image, there won't be any problem.
as a highlight: the code will look for the exact word given, so it depends on the user to type it properly

As it stands now, the code will do its proper analysis and save a version with all the adequate highlights into the
'logs' directory. It is intended for later developing stages that the code will be able to give the option to the user to
save both the image and a text log of all the results, but as of now, the code will only log the current output image

As of now, the main function or command the code can execute is the next one:

'Look 7 orange,cyan waterdrop,moreoptions true test'


please note that the whole command is separated by spaces, these are used to determine which parameters are which so its important to maintain
proper spaces only in between the fragments of the command and not in other places:

'look' : Is the initial word that defines the structure and objective of the whole command; "look" for specific patterns

'7' : Used only in this developing mode to test the rest of the functions; This number can range from 1 to 20 and it refers to its
appropriate template image located in the 'templates' directory

'orange,cyan' : Its the list of colors the user is looking for, it is important that they keep this structure: each color separated
by a comma and without any spaces in between them, that way the code can turn this into a list it can use

'waterdrop,moreoptions' : Its the list of icons or patterns the user is looking for, they maintain the same structure as with the colors,
and for the whole repertoire of options, one can refer to the "icons" directory

'true' : its to indicate to the code that there are specific keywords that the user is looking for, typing true will add a second input
space to open, so the user can type the keywords they are looking for, separated by commas, without any spaces between them, ie:

	'Following,Schedule'

'test' : The last word of the command will be referred to the name the user wishes to give to the output logs.


#ADDENDUMS:

This is a very WIP file with the only purpose to quickly explain the main functions of the code, a proper document is in progress that will have a better 
structure and description to every command
