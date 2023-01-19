#Author: Michael Zylka
#Date: 9/18/2022

import sys
import getopt
from os.path import exists
from PIL import Image

#converts the binary data into binary strings
def _binaryString(data):
    newData = []

    for i in data:
        newData.append(format(ord(i), '08b'))

    return newData

#encodes mf into cf
def encodeFile(cf, mf, sm, sk):
    stego_image = cf.copy()
    data = mf
    dataBinary = _binaryString(data)
    sk = int(sk)

    width = stego_image.size[0]
    (x , y) = (0, 0)
    imageData = iter(stego_image.getdata())
    dataLen = len(dataBinary)


    #adjust for stegonography key
    for i in range(sk):
        if (x == width - 1):
            x = 0
            y += 1
        else: 
            x += 1
        temp = imageData.__next__()[:3]
     
    #iterate through message data
    for i in range(dataLen):
        pixels = []
        
        #group pixels into 9 values
        for j in range(3):
            pixels += imageData.__next__()[:3]

        #iterate though first 8 and encode the message data into the pixels
        if (sm == "LSB"):
            for j in range(8):
                if (dataBinary[i][j] == "0" and pixels[j] % 2 == 1):
                    pixels[j] -= 1
                elif(dataBinary[i][j] == "1" and pixels[j] % 2 == 0):
                    pixels[j] += 1
            #check to see if iterated though all of the message data and 
            #encode 0 or 1 into the 9th bit
            #0 means keep reading, 1 means we finished the message
            if (i == dataLen - 1):
                if (pixels[-1] % 2 ==0):
                    pixels[-1] += 1
            else:
                if (pixels[-1] % 2 == 1):
                    pixels[-1] -= 1
        else:
            for j in range(8):
                if (dataBinary[i][j] == "0" and pixels[j] >= 128):
                    pixels[j] -= 128
                elif(dataBinary[i][j] == "1" and pixels[j] < 128):
                    pixels[j] += 128

            if (i == dataLen - 1):
                if (pixels[-1] < 128):
                    pixels[-1] += 128
            else:
                if (pixels[-1] >= 128):
                    pixels[-1] -= 128

        #check to see if iterated though all of the message data and 
        #encode 0 or 1 into the 9th bit
        #0 means keep reading, 1 means we finished the message
        
        #insert pixels into file
        for j in range(0, len(pixels), 3):
            stego_image.putpixel((x, y), (pixels[j], pixels[j+1], pixels[j+2]))
            if (x == width - 1):
                x = 0
                y += 1
            else: 
                x += 1

    newName = input("Please enter the name of the new stegonography file excluding the extension: ") + ".bmp"
    stego_image.save(newName, "BMP")

#decodes data from 
def decodeFile(cf, mf, sm, sk):
    imageData = iter(cf.getdata())
    width = cf.size[0]
    (x , y) = (0, 0)
    messageData =""
    sk = int(sk)

    #adjust for stegonography key
    for i in range(sk):
        if (x == width - 1):
            x = 0
            y += 1
        else: 
            x += 1
        temp = imageData.__next__()[:3]

    while (True):
        pixels = []
        
        #group pixels into 9 values
        for j in range(3):
            pixels += imageData.__next__()[:3]
        binaryData = ""

        #extract data for LSB stego
        if(sm == "LSB"):
            for i in pixels[:8]:
                if (i % 2 == 0):
                    binaryData += '0'
                else:
                    binaryData += '1'
            messageData += chr(int(binaryData, 2))
            if (pixels[-1] % 2 == 1):
                break
                
        #extract data for MSB stego
        else:
            for i in pixels[:8]:
                if (i >= 128):
                    binaryData += '1'
                else:
                    binaryData += '0'
            messageData += chr(int(binaryData, 2))
            if (pixels[-1] >= 128):
                break

    mf.write(messageData)



#main function
def main(argv):
    print('''
 ______     __     __    __     ______   __         ______     ______     ______   ______     ______     ______    
/\  ___\   /\ \   /\ "-./  \   /\  == \ /\ \       /\  ___\   /\  ___\   /\__  _\ /\  ___\   /\  ___\   /\  __ \   
\ \___  \  \ \ \  \ \ \-./\ \  \ \  _-/ \ \ \____  \ \  __\   \ \___  \  \/_/\ \/ \ \  __\   \ \ \__ \  \ \ \/\ \  
 \/\_____\  \ \_\  \ \_\ \ \_\  \ \_\    \ \_____\  \ \_____\  \/\_____\    \ \_\  \ \_____\  \ \_____\  \ \_____\ 
  \/_____/   \/_/   \/_/  \/_/   \/_/     \/_____/   \/_____/   \/_____/     \/_/   \/_____/   \/_____/   \/_____/ 
                                                                                                                   ''')

    #get input to check if user is encoding or decoding
    encdec = None
    while(encdec != 1 and encdec != 2):
        print('''Please select an option: 
        1. encode
        2. decode
            ''')
        try:
            encdec = int(input())
            print()
        except:
            print()
            print("Invalid input")


    #get input for cover file 
    cover_file = input("Please enter the cover image file name: ")
    try:
        cf = Image.open(cover_file, 'r')
    except FileNotFoundError:
        print("The file does not exist. Exiting program.")
        return

    #get file or text for secret message for encoding
    if (encdec == 1):
        message_file = input("Please enter the secret message or supply the message file (file name cannot have spaces): ")
        if((not " " in message_file) and ("." in message_file)):
            try:
                mf = open(message_file, 'r')
                mf = mf.read()
            except FileNotFoundError:
                print("The file does not exist. Exiting program.")
                return
        else:
            mf = message_file
    
    #determine how the secret message is being displayed
    if (encdec == 2):
        message_file = input("Please enter the name of the output file for the secret message (leave empty if you want it to print in the terminal): ")
        if(message_file == "" or message_file == " "):
            mf = sys.stdout
        else:
            try:
                mf = open(message_file, "x")
            except FileExistsError:
                print("The file already exists. Exiting program.")
                return

    #get the stegonography mode
    stego_mode = None
    while (stego_mode != "LSB" and stego_mode != "MSB"):
        stego_mode = input("Enter the Stegonagraphy mode (LSB, MSB): ").upper()
        if(stego_mode != "LSB" and stego_mode != "MSB"):
            print("Invalid Input")
            print()

    #Get the stegonography key 
    stego_key = None
    while(stego_key == None):
        try:
            stego_key = input("Enter the Stegonography key: ")
            print()
        except:
            print()
            print("Invalid input. Stegonography key must be a number.")
            stego_key = None
    
    if (encdec == 1):
        encodeFile(cf, mf, stego_mode, stego_key)
    else:
        decodeFile(cf, mf, stego_mode, stego_key)
            

if __name__ == "__main__":
    main(sys.argv[1:])