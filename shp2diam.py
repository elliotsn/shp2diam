#!/bin/python
#
# Python program to convert a shapefile containing craters into a format readable
# by craterstats2
#
# Elliot Sefton-Nash  2015/03/09
#
def usage():
    print """
    Program to convert craters stored as polygons in a shapefile to a .diam file
    that is readable by the IDL program craterstats.
    
    USAGE:
        shp2diam [FILENAME]

    Where FILENAME is the path to the shapefile.
    
    If the following columns are present in any combination of character case 
    the program will include them in the output file:

        diameter|diam|d
        radius|rad|r
        latitude|lat
        longitude|lon  
        
    Elliot Sefton-Nash (e.sefton-nash@uclmail.net)

    """
    exit()
 
 
def getHeader():
    return """
#  diam file written by shp2diam
#  Elliot Sefton-Nash
#
# Area (km^2). Edit this value according to the area covered by this crater
# distribution.
area = 1
#
# Table below may include any of the following field combinations:
#
#              km        -      deg  deg
# crater = {diameter
# crater = {diameter, fraction
# crater = {diameter, fraction, lon, lat
#"""
 
#
# Function to return the field line based on the contents of a shapefile.
# fshp is a shapefile reader object, outcols is a list of column numbers.
#
def getFieldStr(fshp, outcols):
    fieldStr=''
    piece='{'
    for c in outcols:
        # Remove '+1' if deletion flag not present.
        fieldStr += piece+fshp.fields[c+1][0]
        piece = ', '
    return fieldStr

#
# Function to write .diam format to stdout.
#
def printDiam(fshp, outcols, scale):

    from sys import stdout
    import numpy as np

    # Write the header
    print >> stdout, getHeader()
    
    # Write the table    
    print >> stdout, 'crater = '+getFieldStr(fshp, outcols)
    
    # Put in numpy array
    numCols = len(outcols)
    numRecs = fshp.numRecords
    a = np.zeros((numRecs,numCols))
    for r in range(numRecs):
        for c in range(numCols):
            a[r, c] = float(fshp.record(r)[outcols[c]])
    
    # Now scale the data accordingly
    for i,sca in enumerate(scale):
        a[:,i] *= sca
    
    # Print formatted.
    for r in range(numRecs):
        l=''
        piece=''
        for c in range(numCols):
            l += piece+"{:12.6f}".format(a[r,c])
            piece=','
        print >> stdout, l

    # Closing brace
    print >> stdout, '}'


if __name__ == '__main__':

    try:
        import shapefile
        from sys import argv

    except:
        print 'pyshp is not installed. You must install the pyshp module.'
        exit()

    # If there is not one argument then only display the usage.
    if (len(argv) != 2):
        usage()
    else:
        # Read filelist into python list.
        fpath=argv[1]
    
    # testing
    #fpath='/Users/elliotsefton-nash/workspace/craters/hypanis_delta/hypanis_craters_polygon_CTX.shp'

    try:
        fshp = shapefile.Reader(fpath)
    except:
        print 'Error opening file '+fpath
        exit()
    
    # List of tuples, each tuple contains different possible forms of the same 
    # field.
    # Must separate, makes easier to remove tuple from super-tuple.
    fields = [['latitude','lat',],
              ['longitude','lon',],
              ['radius','rad','r',],
              ['diameter','diam','d',],]
    #fields = [['diameter','diam','d',], ]
 
    ## offset is used because DeletionFlag is listed at the start of the
    ## shapefile but isn't included in the table.
  
    # Is each column in the list of fields? If so add it to the output columns.
    outcols = []
    scale = []
    #fields = fshp.fields
    for i,col in enumerate(fshp.fields):        
        for f in fields:
            if f.__contains__(col[0].lower()):
                # Remove -1 if deletionflag not present.
                outcols.append(i-1)
                
                # Decide which fields to scale, i.e. to convert from m to km.
                if (f[0] == 'radius') | (f[0] == 'diameter'):
                    scale.append(1./1000.)
                else:
                    scale.append(1.)
                
                # Remove the field detected so we don't risk double-detection.
                fields.remove(f)
                break
    
    # Write the output file
    if len(outcols) == 0:
        print 'No useful fields found. File not written.'
        exit()
    else:
        # Pass the reader object and outcols to printDiam
        printDiam(fshp,outcols,scale)
        exit()
