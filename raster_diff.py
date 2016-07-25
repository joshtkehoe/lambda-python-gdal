import os
import numpy as np
from osgeo import gdal, osr
from PIL import Image
from PIL import ImageDraw
'''
    This application is called from a Lambda function to generate a change .png using two S3 .tifs as inputs.
    IMPORTANT: Anything printed to standard out will be returned to raster-diff-lambda-function. ONLY print
    out the JSON result at the end, do not do any print debug statements.
'''

def process():
    # do stuff
    pass

def main():
    # Do your GDAL stuff here. Store whatever you want your Lambda to return in the result var and print it out.
    result = process()

    # This should be the only print statement in this application.
    print result
    return result

if __name__ == '__main__':
    main()

