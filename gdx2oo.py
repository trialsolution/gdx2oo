#!/usr/bin/python

import sys
import getopt
import readgdx




def CreateColumnNames():
    #creating Column labels
    #from AA to IV
    from string import ascii_uppercase

    abc = ascii_uppercase
    #ColumnNames=[]
    
    global _column_names
    global _number_of_rows
    _number_of_rows=65536
    _column_names=[]

    ##AA to HZ
    for i in abc[0:8]:
        for j in abc:
            #ColumnNames.append(i+j)
            _column_names.append(i+j)
       
    ##IA to IV
    for i in abc[0:-4]:
        #ColumnNames.append("I"+i)
        _column_names.append("I"+i)
       
    #Number of Rows
    #NumberOfRows = 65536
    
    #print(ColumnNames)
def main(argv):
    targetfile=""
    IsHeader="Yes"
    scalarsheet="Yes"
    try:
        opts, args = getopt.getopt(argv, "hH:t:s:", ["help", "Header=", "Target=", "Scalarsheet="])
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
                break
            elif opt in ("-H", "--Header"):
                IsHeader=arg[1:]
                #print "header" + IsHeader
            elif opt in ("-t", "--Target"):
                targetfile=arg[1:]
            elif opt in ("-s", "--Scalarsheet"):
                scalarsheet=arg[1:]
                #print "scalarsheet" + scalarsheet
        dumpfile = "".join(args)
        if dumpfile=="":
            #sys.exit(2)
            dumpfile="trnsport.dump" #for testing purposes PLEASE REMOVE!!!!!!!!!!!!!!
        if targetfile=="":
            WithoutExt=str(dumpfile.split(".")[0])
            targetfile=WithoutExt + ".ods"
        w = readgdx.GdxContent(dumpfile)
        #w.WriteAll(header=IsHeader, scalarsheet=scalarsheet)
        w.WriteAll();
        #print "targetfile" + targetfile
        w.SaveOOFile(targetfile)      
    except getopt.GetoptError:
        usage()
        sys.exit(2)

def usage():
    """
        Print out basic help to the console
    """
    print( 
    """Available flags:
    -h, --help: prints out this message
    -H, --Header: indicates that output contains headers
    -t, --Target: specifies output file name
Examples:
    gdx2oo.py -H No trnsport.dump
    gdx2oo.py -t result.ods trnsport.dump """)
    
    
if __name__=="__main__":
    main(sys.argv[1:])
    """
        Usage examples: 
                        gdx2oo.py -H No trnsport.dump
                        gdx2oo.py -t result.ods trnsport.dump
    """
    #CreateColumnNames()
    
