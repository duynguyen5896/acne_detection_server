import cv2 as cv
#from pyimagesearch import imutils
import numpy as np
import sys
import os
import shutil
import traceback
from os.path import isfile, join
def skDetection(image):
    min_YCrCb = np.array([0,133,77],np.uint8)
    max_YCrCb = np.array([235,173,127],np.uint8)

    # Get pointer to video frames from primary device
    
    imageYCrCb = cv.cvtColor(image,cv.COLOR_BGR2YCR_CB)
    skinRegionYCrCb = cv.inRange(imageYCrCb,min_YCrCb,max_YCrCb)

    skinYCrCb = cv.bitwise_and(image, image, mask = skinRegionYCrCb)
    return skinYCrCb
def skindetection(img,lower, upper):
    img = imutils.resize(img, width = 250)
    converted = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    skinMask = cv.inRange(converted, lower, upper)
	# apply a series of erosions and dilations to the mask
	# using an elliptical kernel
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (11, 11))
    skinMask = cv.erode(skinMask, kernel, iterations = 2)
    skinMask = cv.dilate(skinMask, kernel, iterations = 2)
 
	# blur the mask to help remove noise, then apply the
	# mask to the frame
    skinMask = cv.GaussianBlur(skinMask, (3, 3), 0)
    skin = cv.bitwise_and(img, img, mask = skinMask)
    cv.imshow("skin detector", skin)
    return skin
def findPimples(img,filename,resultpath):
    # define the upper and lower boundaries of the HSV pixel
    # intensities to be considered 'skin'
    # ---Skin Detection
    
    #lower = np.array([0, 48, 80], dtype = "uint8")  
    #upper = np.array([20, 255, 255], dtype = "uint8")
    #img = skindetection(img, lower, upper) 
    #img = skDetection(img)
    #cv.imshow("aaaa",img)
    #cv.waitKey(0)
    
    
    #finding pimples
    
    #---Get data of green channel
   
    bgr = cv.split(img)
    bw = bgr[1]
    pimplescount = 0
    
    #---Blur (Smooth) the image to remove noise
    bw = cv.GaussianBlur(bw,(5,5),cv.BORDER_DEFAULT)
    #cv.imshow("pimples detector 2", bw)
    bw =  cv.adaptiveThreshold(bw,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,15,5)
    #cv.imshow("pimples detector", bw)
    #cv.waitKey(0)
    dilate = cv.dilate(bw, (-1,-1),1)
    contours, _ = cv.findContours(bw, cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv.contourArea(contour)
        if(area > 20):
            x,y,w,h = cv.boundingRect(contour)
            minRect = cv.boundingRect(contour)
            imgroi = img[y:y+h,x:x+w]
            imgroi = cv.cvtColor(imgroi,cv.COLOR_BGR2HSV)
            color = cv.mean(imgroi)
            imgroi = cv.cvtColor(imgroi,cv.COLOR_HSV2BGR)
            #if(color[0] < 10 and color[1] > 70 and color[2] > 50):
            (x,y), radius = cv.minEnclosingCircle(contour)
            center = (int(x),int(y))
            radius = int(radius)
            if(radius <20):
                cv.rectangle(img,minRect,(0,255,0))
                pimplescount+=1
    cv.putText(img,str(pimplescount),(50,30),cv.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2,cv.LINE_AA)
    #cv.imshow("pimples detector",img)
    cv.imwrite(resultpath+filename+"_result.jpg",img)
def main():
    #try:
        userID = sys.argv[1]
        sessionID = sys.argv[2]
        #---Setup directory
        mypath = os.path.dirname(os.path.abspath(__file__))
        imagepath = mypath+"\\images\\"+userID+"\\"+sessionID+"\\"
        resultpath = imagepath+ "\\results\\"
        if os.path.exists(resultpath):
            shutil.rmtree(resultpath) #Remove old result
        #---Generate results folder
        os.makedirs(resultpath)
        #---Load all images in folder
        files = os.listdir(imagepath)
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg')):
                #print(file)
                src = cv.imread(imagepath+file)
                if src is None:
                    print("Cannot load the image. Please check the image manually and retry again!!!")
                    return
                #cv.namedWindow("pimples detector",cv.WINDOW_AUTOSIZE)
                cloneimg = src.copy()
                #cv.imshow("pimples detector",src)
                filename= os.path.splitext(file)[0]
                #-----Do Magic--------
                findPimples(cloneimg,filename,resultpath)
                #cv.waitKey(0)
        print("done!")
    #except Exception as e:
    #    print("Exception:", e)
main()