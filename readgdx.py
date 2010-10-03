#! /usr/bin/python

import ooolib

default_options={'value_bg':"#FFFF99",
'value_fg':"#000000",
'header_bg':"#33CCFF",
'header_fg':"#660000",
'header':'Yes',
'scalarsheet':'Yes',
'clear_dump':'Yes',
'header':'Yes', 
'scalarsheet':'Yes'
}

#initializing
global gdx2oo_options
gdx2oo_options = default_options

def look_costum_config():
    configfile="gdx2oo.conf"
    config_content=[]
    try:
        fs = open(configfile, 'r')    
        while 1:
            txt = fs.readline()
            #empty line indicates the EOF
            if txt == '':
                break            
            stt=[]
            stt.append(txt)
            stt[-1] = stt[-1].strip('\n') #new line characters removed
            config_content.extend(stt)
        fs.close()
        #config file read
        print config_content
    except:
        #No config file
        print "Configuration file not found"
    return config_content
    
def change_colors(clist):
    if clist==[]:
        exit
    else:
        #look for [colors]
        global gdx2oo_options
        i = clist.index('[colors]')+1
        while clist[i] != '' and clist[i][0] != '[' and i < len(clist): 
            if clist[i].split('=')[0] == 'value_bg':
                gdx2oo_options['value_bg'] = clist[i].split('"')[1]
            elif clist[i].split('=')[0] == 'value_fg':
                gdx2oo_options['value_fg'] = clist[i].split('"')[1]
            elif clist[i].split('=')[0] == 'header_bg':
                gdx2oo_options['header_bg'] = clist[i].split('"')[1]
            elif clist[i].split('=')[0] == 'header_fg':
                gdx2oo_options['header_fg'] = clist[i].split('"')[1]
            i += 1
    
def change_settings(clist):
    if clist==[]:
        exit
    else:
        #looking for settings
        global gdx2oo_options
        i = clist.index('[settings]')+1
        while i<len(clist):
            if clist[i] != '' and clist[i][0] != '[':
                if clist[i].split('=')[0] == 'header':
                    gdx2oo_options['header'] = clist[i].split('"')[1]
                elif  clist[i].split('=')[0] == 'scalarsheet':
                    gdx2oo_options['scalarsheet'] = clist[i].split('"')[1]
            i += 1
            
    
class GdxContent():
    def __init__(self, filename):
        self.X=[]
        self.gamsVar=[] #gams variables
        self.keywords=['Set', 'Equation', 'Parameter', 'Variable', 'Scalar']
        self.VarNames=[]
        self.VarKeyword=[]
        self.VarDescription=[]
        self.VarDimension=[]
        self.Y=[] #will contain elementary data
        #data extraction and variable identification
        self.extract(filename)
        self.findvariables()
        self.identifyvariables()
        self.FillY()
        self.doc = ooolib.Calc()
        change_colors(look_costum_config())
        change_settings(look_costum_config())
        self.options = gdx2oo_options #dictionary of options
    
    def set_colors(self, target):
        if target == "header":
            self.doc.set_cell_property('color', self.options['header_fg'])
            self.doc.set_cell_property('background', self.options['header_bg'])
        elif target == "value":
            self.doc.set_cell_property('color', self.options['value_fg'])
            self.doc.set_cell_property('background', self.options['value_bg'])
        elif target == "default":
            self.doc.set_cell_property('color', 'default')
            self.doc.set_cell_property('background', 'default')
            
                
        
    def FillY(self):
        """
            Y contains elementary data
        """
        #initialize Y
        #an empty list with exatly as many elements as gams variables exist
        for i in self.gamsVar:
            self.Y.append('')
        for el in range(0, len(self.VarKeyword)):
            if self.VarKeyword[el] == 'Scalar':
                try: 
                    y = str(self.gamsVar[el]).split('/')
                    self.Y[el] = float(y[1])
                except:
                    print("Scalar value not found")
            if self.VarKeyword[el] == 'Set':
                try:
                    x=[]
                    for line in range(1, len(self.gamsVar[el])): #first row does not contain values
                        linestr = str(self.gamsVar[el][line])
                        splittedLine = linestr.split("'")
                        x.append(splittedLine[1])
                    self.Y[el]=x
                except:
                    print("Set values not found")
            if self.VarKeyword[el] == 'Parameter':
                try:
                    x=[]
                    for line in range(1, len(self.gamsVar[el])): #first row does not contain values
                        linestr = str(self.gamsVar[el][line])
                        splittedLine = linestr.split(' ')
                        identifiers = splittedLine[0]
                        if self.VarDimension[el] > 1 :
                            identifiers2 = identifiers.split('.') #at least two dimensional parameters
                            for id in identifiers2:
                                x.append(id.split("'")[1])
                        else:
                            x.append(identifiers.split("'")[1])
                        value = splittedLine[1]
                        if value[-1] == ',':
                            value = value.strip(',')
                            x.append(float(value))
                        else:
                            value = value.strip('/;')
                            x.append(float(value))
                    self.Y[el] = x
                except:
                    print("Parameter values not found")
            if self.VarKeyword[el] == 'Variable' or self.VarKeyword[el] == 'Equation':
                try:
                    if self.VarDimension[el] == 0:
                        x=[]
                        linestr = str(self.gamsVar[el][0])
                        splittedLine = linestr.split('/')
                        identifier = splittedLine[1].split(' ')[0]
                        x.append(identifier)
                        try:
                            value= float(splittedLine[1].split(' ')[1])
                        except:
                            value= splittedLine[1].split(' ')[1]
                        x.append(value)    
                        self.Y[el] = x 
                        
                    else:
                        x=[]
                        for line in range(1, len(self.gamsVar[el])):
                            linestr = str(self.gamsVar[el][line])
                            splittedLine = linestr.split(' ')
                            identifiers = splittedLine[0]
                            identifiers2 = identifiers.split('.') 
                            for id in identifiers2:
                                if len(id.split("'"))>1:
                                    x.append(id.split("'")[1])
                                else:
                                    x.append(id)
                            value = splittedLine[1]
                            if value[-1] == ',':
                                value = value.strip(',')
                                try:
                                    #if the marginal or level is a real number
                                    x.append(float(value))
                                except:
                                    x.append(value)
                            else:
                                value = value.strip('/;')
                                try:
                                    #if the marginal or level is a real number
                                    x.append(float(value))
                                except:
                                    x.append(value)
                        self.Y[el] = x
                except:
                    print("Variable values not found")
        
    def PrintY(self):
        print("\nY in raw form:\n")
        for i in self.Y:
            print i
        
    def extract(self, filename):
        """
            Extracts the content of a gdxdump file
            Needs an input file generated with 'gdxdump gdxfile.gdx Output=dumpfile'
        """
        try:
            fs = open(filename, 'r')    
        except:
            print "Dumpfile can not be opened"
        #writing the content of dumpfile into the self.X
        while 1:
            txt = fs.readline()
            #empty line indicates the EOF
            if txt == '':
                break            
            #stt = txt.split(" ") #line splitted among empty chars
            stt=[]
            stt.append(txt)
            stt[-1] = stt[-1].strip('\n') #new line characters removed
            self.X.append(stt)
        fs.close()
        print "File %s extracted" % filename
        
    def PrintGamsVariables(self):
        print("\nGams Variables:\n")
        for i in range(len(self.gamsVar)):
            print(str(self.gamsVar[i])+"\n")
            
    def PrintX(self):
        print("\nX in raw form:\n")
        print(self.X)
        
    def PrintTheWhole(self):
        print("\nThe Whole X:\n")
        for i in range(len(self.X)):
            print(str(self.X[i])+"\n")
    
    def findvariables(self):
        """
            Finds gams variables in X
            Variables are separated by empty lines in the dump files (and by empty elements in X)
        """
        myvariable=['']
        for i in range(1, len(self.X)):
            if self.X[i] == self.X[0]:
                self.gamsVar.append(myvariable[1:])    
                myvariable=[]
            myvariable.append(self.X[i])
        self.gamsVar.append(myvariable[1:]) #append the last one        
        #create lists for variable specs (name, keyword)
        #specs are set in method identifyvariables()
        for i in self.gamsVar:
            self.VarNames.append('')
            self.VarKeyword.append('')
            self.VarDescription.append('')
            self.VarDimension.append('')
    
    def identifyvariables(self):
        """
            Identifies variable names and types (equation, parameter etc.)
        """   
        for el in range(len(self.gamsVar)):
            actVariable = self.gamsVar[el]
            actList = actVariable[0][0].split(' ')
            try:
                for i in range(len(actList)):
                    identified=False
                    for j in self.keywords:
                        if actList[i]==j:               
                            #print(actList[i], " in position: %i" %i)
                            #print(str(actList[i])+ " " + str(actList[i+1]))
                            self.VarKeyword[el] = j
                            #self.VarNames[el] = str(actList[i+1])
                            self.VarDimension[el] = self.DefineDimension(actList[i+1])
                            #print(self.VarDimension[el])
                            self.VarNames[el] = self.DefineVarName(actList[i+1])
                            #print(self.VarNames[el])
                            self.VarDescription[el] = self.FindDescription(actList, i+2)
                            #print(self.VarDescription[el])
                            identified=True
                            break
                    if identified==True:
                        break
                if identified==False:
                        print("Variable can not be identified")
            except:
                print("Error by identification")         

    def FindDescription(self, mylist, myposition):
        """ 
            Finds a forward slash in a given list
            starting from a given position
        """
        description = ""
        i = myposition
        while i < len(mylist):
            if mylist[i][0] == "/":
                break
            description = description + str(mylist[i]) + " "
            i += 1
        return description
                


                
    def PrintHeader(self):
            print("\nHeader:\n")
            for i in range(len(self.VarNames)):
                print(str(self.VarKeyword[i])+" "+ str(self.VarNames[i]) + ": " + str(self.VarDescription[i]))
    
           
                
    def WriteTOC(self):
        #self.doc.set_sheet_index(0)
        sheet = self.doc.sheets[0]
        sheet.set_name("TOC")
        self.doc.set_cell_property('color', self.options['header_fg'])
        self.doc.set_cell_property('background', self.options['header_bg'])
        #title
        row = 1
        col = 1
        self.doc.set_cell_property('bold', True)
        self.doc.set_cell_value(col, row, "string", "Table Of Contents")
        #table header
        row = 2
        col = 1
        self.doc.set_cell_value(col, row, "string", "Variable Name")
        col += 1
        self.doc.set_cell_value(col, row, "string", "Type")
        col += 1
        self.doc.set_cell_value(col, row, "string", "Dimension")
        col += 1
        self.doc.set_cell_value(col, row, "string", "Description")
        self.doc.set_cell_property('bold', False)
        self.doc.set_cell_property('color', 'default')
        self.doc.set_cell_property('background', 'default')
        
        self.doc.set_cell_property('color', self.options['value_fg'])
        self.doc.set_cell_property('background', self.options['value_bg'])
        #Variables headers
        row = 3
        col = 1
        for i in range(0, len(self.gamsVar)):
            #self.doc.set_cell_value(col, row, "string", str(self.VarNames[i]))
            self.doc.set_cell_value(col+1, row, "string", str(self.VarKeyword[i]))
            self.doc.set_cell_value(col+2, row, "string", str(self.VarDimension[i]))
            self.doc.set_cell_value(col+3, row, "string", str(self.VarDescription[i]))
            row += 1
        self.doc.set_cell_property('color', 'default')
        self.doc.set_cell_property('background', 'default')

    

    def SaveOOFile(self, targetfile):    
        #save file
        self.doc.save(targetfile)
        
    def WriteSet(self, setname, header="Yes"):
        #get set index
        setindex = self.VariableIndex(setname)
        if setindex == -1:
            print "Set %s is not found" % setname
        else:
            self.doc.new_sheet(setname)
            self.doc.set_cell_value(1,1,"link", ('#TOC', 'TOC'))
            row = 2
            col = 1
            #header
            if header!="No":
                self.doc.set_cell_property('color', self.options['header_fg'])
                self.doc.set_cell_property('background', self.options['header_bg'])
                self.doc.set_cell_property('bold', True)
                self.doc.set_cell_value(col, row, "string", str(self.VarNames[setindex]))
                col+=1
                self.doc.set_cell_property('bold', False)
                self.doc.set_cell_value(col, row, "string", "(" + str(self.VarKeyword[setindex]) + ")")
                col+=1
                self.doc.set_cell_property('italic', True)
                self.doc.set_cell_value(col, row, "string", str(self.VarDescription[setindex]))
                self.doc.set_cell_property('italic', False)
                row += 1
                col = 1
                self.doc.set_cell_property('color', 'default')
                self.doc.set_cell_property('background', 'default')

            #values
            self.doc.set_cell_property('color', self.options['value_fg'])
            self.doc.set_cell_property('background', self.options['value_bg'])
            y = self.Y[setindex]
            for i in y:
                if type(i) == float:
                    self.doc.set_cell_value(col, row, "float", i)
                else:
                    self.doc.set_cell_value(col, row, "string", i)
                row+=1
            self.doc.set_cell_property('color', 'default')
            self.doc.set_cell_property('background', 'default')
    
    def WriteScalar(self, scalarname, header="Yes", scalarsheet="Yes"):
        #get scalar index
        scalarindex = self.VariableIndex(scalarname)
        if scalarindex == -1:
            print "Scalar %s is not found" % scalarname
        else:
            if scalarsheet != "No": #this is the default
                sheetindex = self.FindSheet("scalars")
                if sheetindex >-1:
                    self.doc.set_sheet_index(sheetindex)
                    (cols, rows) = self.doc.get_sheet_dimensions()
                    row = rows+1
                    col=1
                    self.doc.set_cell_value(col, row, "string", str(self.VarNames[scalarindex]))
                    col+=1
                    if type(self.Y[scalarindex])==float:
                        self.doc.set_cell_value(col, row, "float", self.Y[scalarindex])
                    else:
                        self.doc.set_cell_value(col, row, "string", self.Y[scalarindex])
                else:
                    print "Sheet 'scalars' not created"
    
            else:
                self.doc.new_sheet(scalarname)
                self.doc.set_cell_value(1,1,"link", ('#TOC', 'TOC'))
                row = 2
                col = 1
                #header
                if header!="No":
                    self.doc.set_cell_property('bold', True)
                    self.doc.set_cell_value(col, row, "string", str(self.VarKeyword[scalarindex]) + " " + str(self.VarNames[scalarindex]))
                    self.doc.set_cell_property('bold', False)
                    row += 1
                #values
                if type(self.Y[scalarindex])==float:
                    self.doc.set_cell_value(col, row, "float", self.Y[scalarindex])
                else:
                    self.doc.set_cell_value(col, row, "string", self.Y[scalarindex])
    
    def FindSheet(self, sheetname):
        count = self.doc.get_sheet_count()
        for c in range(0, count):
            self.doc.set_sheet_index(c)
            if sheetname == self.doc.get_sheet_name():
                return c
        return -1 #sheet not found
            
    
    
    def WriteParameter(self, parname, header="Yes"):
        parindex = self.VariableIndex(parname)
        if parindex == -1:
            print "Parameter %s is not found" % parname
        else:
            self.doc.new_sheet(parname)
            self.doc.set_cell_value(1,1,"link", ('#TOC', 'TOC'))
            pardim = self.VarDimension[parindex] + 1 
            row = 2
            col = 1
            #header
            if header!="No":
                self.doc.set_cell_property('color', self.options['header_fg'])
                self.doc.set_cell_property('background', self.options['header_bg'])
                self.doc.set_cell_property('bold', True)
                self.doc.set_cell_value(col, row, "string", str(self.VarNames[parindex]))
                col+=1
                self.doc.set_cell_property('bold', False)
                self.doc.set_cell_value(col, row, "string", "(" + str(self.VarKeyword[parindex]) + ")")
                col+=1
                self.doc.set_cell_property('italic', True)
                self.doc.set_cell_value(col, row, "string", str(self.VarDescription[parindex]))
                self.doc.set_cell_property('italic', False)
                row += 1
            #variable properties    
            self.doc.set_cell_property('bold', True)
            col = 1
            while col <(pardim):
                self.doc.set_cell_value(col, row, 'string', "dim"+str(col))
                col += 1
            self.doc.set_cell_property('halign', 'right')
            self.doc.set_cell_value(col, row, "string", "LEVEL")
            self.doc.set_cell_property('bold', False)
            self.doc.set_cell_property('halign', 'default')
            
            col = 1
            row += 1
            #values
            self.doc.set_cell_property('color', self.options['value_fg'])
            self.doc.set_cell_property('background', self.options['value_bg'])
            y = self.Y[parindex]
            pardim = self.VarDimension[parindex] + 1 
            for i, el in enumerate(y):
                if (i+1)%pardim >0:
                    self.doc.set_cell_value(col, row, "string", el)
                    col += 1
                if (i+1)%pardim ==0: 
                    try:
                        self.doc.set_cell_value(col, row, "float", el)
                    except:
                        self.doc.set_cell_value(col, row, "string", el)
                    #new line
                    row+=1
                    col = 1
                    
                    
    def WriteVariable(self, varname, header="Yes"):
        varindex = self.VariableIndex(varname)
        vardim = self.VarDimension[varindex] + 1 
        if varindex == -1:
            print "Variable %s is not found" % varname
        else:
            self.doc.new_sheet(varname)
            self.doc.set_cell_value(1,1,"link", ('#TOC', 'TOC'))
            y = self.Y[varindex]
            vardim = self.VarDimension[varindex] + 2
            row = 2
            col = 1
            #header
            if header!="No":
                self.doc.set_cell_property('color', self.options['header_fg'])
                self.doc.set_cell_property('background', self.options['header_bg'])
                self.doc.set_cell_property('bold', True)
                self.doc.set_cell_value(col, row, "string", str(self.VarNames[varindex]))
                col+=1
                self.doc.set_cell_property('bold', False)
                self.doc.set_cell_value(col, row, "string", "(" + str(self.VarKeyword[varindex]) + ")")
                col+=1
                self.doc.set_cell_property('italic', True)
                self.doc.set_cell_value(col, row, "string", str(self.VarDescription[varindex]))
                self.doc.set_cell_property('italic', False)
                #self.doc.set_cell_value(col, row, "string", str(self.VarKeyword[varindex]) + " " + str(self.VarNames[varindex]))    
                row += 1
            #variable properties    
            self.doc.set_cell_property('bold', True)
            col = 1
            while col <(vardim-1):
                self.doc.set_cell_value(col, row, 'string', "dim"+str(col))
                col += 1
            #col += vardim-2
            self.doc.set_cell_property('halign', 'right')
            self.doc.set_cell_value(col, row, "string", "LOWER")
            col += 1
            self.doc.set_cell_value(col, row, "string", "LEVEL")
            col += 1
            self.doc.set_cell_value(col, row, "string", "UPPER")
            col += 1
            self.doc.set_cell_value(col, row, "string", "MARGINAL")
            self.doc.set_cell_property('bold', False)
            self.doc.set_cell_property('halign', 'default')
            col = 1
            row += 1
            
            self.doc.set_cell_property('color', self.options['value_fg'])
            self.doc.set_cell_property('background', self.options['value_bg'])
            
            DistinctValues=[]
            element = []
            for i, el in enumerate(y):
                if (i+1) % vardim < (vardim -1) and (i+1) % vardim > 0: 
                    element.append(el)
                if (i+1) % vardim == vardim - 1:
                    if self.StillHas(DistinctValues, element) != True:
                        DistinctValues.append(element)
                    element = []
                
            
            #Levels -- looking for L-s in y
            Level=[]
            for i, el in enumerate(y):
                if el == 'L':
                    #identifiers
                    for n in range(i-vardim+2, i):
                        Level.append(y[n])
                    #the value
                    Level.append(y[i+1])

            #Lower bounds
            Lower=[]
            for i, el in enumerate(y):
                if el == 'LO':
                    #identifiers
                    for n in range(i-vardim+2, i):
                        Lower.append(y[n])
                    #the value
                    Lower.append(y[i+1])
            
            #Upper bounds
            Upper=[]
            for i, el in enumerate(y):
                if el == 'UP':
                    #identifiers
                    for n in range(i-vardim+2, i):
                        Upper.append(y[n])
                    #the value
                    Upper.append(y[i+1])
                           
            #Marginals
            Marginal=[]
            for i, el in enumerate(y):
                if el == 'M':
                    #identifiers
                    for n in range(i-vardim+2, i):
                        Marginal.append(y[n])
                    #the value
                    Marginal.append(y[i+1])

            #print Level, Marginal, Upper, Lower
        
            
            TLevel=[]
            myRow=""
            for i, el in enumerate(Level):
                if (i+1)%(vardim-1)>0: 
                    myRow += el
                if (i+1)%(vardim-1)==0: 
                    TLevel.append(myRow)
                    TLevel.append(el)
                    myRow=""
            
            TMarginal=[]
            myRow=""
            for i, el in enumerate(Marginal):
                if (i+1)%(vardim-1)>0: 
                    myRow += el
                if (i+1)%(vardim-1)==0: 
                    TMarginal.append(myRow)
                    TMarginal.append(el)
                    myRow=""
                     
            TUpper=[]
            myRow=""
            for i, el in enumerate(Upper):
                if (i+1)%(vardim-1)>0: 
                    myRow += el
                if (i+1)%(vardim-1)==0: 
                    TUpper.append(myRow)
                    TUpper.append(el)
                    myRow=""
                    
            TLower=[]
            myRow=""
            for i, el in enumerate(Lower):
                if (i+1)%(vardim-1)>0: 
                    myRow += el
                if (i+1)%(vardim-1)==0: 
                    TLower.append(myRow)
                    TLower.append(el)
                    myRow=""
            
            
            #print TLevel, TMarginal, TUpper, TLower
            
            for j in DistinctValues:
                myconcat=""
                for k in j:
                    self.doc.set_cell_value(col, row, "string", k)
                    col += 1
                    myconcat+=k  
                #Lower
                if self.LookUpValue(TLower, myconcat) != False:
                    try:
                        self.doc.set_cell_value(col, row, "float", self.LookUpValue(TLower, myconcat))
                    except:
                        self.doc.set_cell_value(col, row, "string", self.LookUpValue(TLower, myconcat))
                col+=1
                #Level
                if self.LookUpValue(TLevel, myconcat) != False:
                    try:
                        self.doc.set_cell_value(col, row, "float", self.LookUpValue(TLevel, myconcat))
                    except:
                        self.doc.set_cell_value(col, row, "string", self.LookUpValue(TLevel, myconcat))
                col+=1
                #Upper
                if self.LookUpValue(TUpper, myconcat) != False:
                    try:
                        self.doc.set_cell_value(col, row, "float", self.LookUpValue(TUpper, myconcat))
                    except:
                        self.doc.set_cell_value(col, row, "string", self.LookUpValue(TUpper, myconcat))
                col+=1
                #Marginal
                if self.LookUpValue(TMarginal, myconcat) != False:
                    try:
                        self.doc.set_cell_value(col, row, "float", self.LookUpValue(TMarginal, myconcat))
                    except:
                        self.doc.set_cell_value(col, row, "string", self.LookUpValue(TMarginal, myconcat))
                col+=1


                row += 1
                col = 1    
    
    def LookUpValue(self, mylist, mystring):
        for i, el in enumerate(mylist):
            if el==mystring:
                return mylist[i+1]
        return False
    def StillHas(self, listoflists, mylist):
        for el in listoflists:
            if el==mylist:
                return True
        return False
                
    def VariableIndex(self, vname):
        RetValue = -1
        for i, el in enumerate(self.VarNames):    
            if el == vname:    
                RetValue = i
        return RetValue
        
    def DefineDimension(self, sstring):
        """
            Examines string whether it contains '('
            and if yes, how many ','-s
        """
        found = False
        i = 0
        while i<len(sstring):
            if sstring[i] == '(':
                found = True
                break
            i += 1
        if found == False:
            return 0
        else:
            sstr2 = sstring.split('(')
            NumberOfCommas = 0
            i = 0
            while i<len(sstr2[1]):
                if sstr2[1][i] == ',':
                    NumberOfCommas += 1
                if sstr2[1][i] == ')':
                    break
                i += 1
            return NumberOfCommas+1
        
        
    def DefineVarName(self, sstring):
        """
            Splits the string among '('
            Takes the first part = variable name
        """
        sstr = sstring.split('(')
        return str(sstr[0])
        
    def WriteAll(self):
        header=self.options['header']
        scalarsheet=self.options['scalarsheet']
        self.WriteTOC() #table of contents without links
        if scalarsheet!="No":
            self.doc.new_sheet("scalars")
            self.doc.set_cell_value(1,1,"link", ('#TOC', 'TOC'))       
        for i, el in enumerate(self.VarNames):
            if self.VarKeyword[i] == 'Set':
                self.WriteSet(el, header)
                self.doc.set_sheet_index(0)
                self.set_colors('value')   
                self.doc.set_cell_value(1, i+3, 'link', ('#'+str(el), str(el)))
                self.set_colors('default')
            if self.VarKeyword[i] == 'Scalar':
                self.WriteScalar(el, header=header, scalarsheet=scalarsheet)
                if scalarsheet!="No":
                    self.doc.set_sheet_index(0)
                    self.set_colors('value')   
                    self.doc.set_cell_value(1, i+3, 'link', ('#scalars', str(el)))
                    self.set_colors('default')   
                else:
                    self.doc.set_sheet_index(0)
                    self.set_colors('value')   
                    self.doc.set_cell_value(1, i+3, 'link', ('#'+str(el), str(el)))
                    self.set_colors('default')   
            if self.VarKeyword[i] == 'Parameter':
                self.WriteParameter(el, header)
                self.doc.set_sheet_index(0)
                self.set_colors('value')   
                self.doc.set_cell_value(1, i+3, 'link', ('#'+str(el), str(el)))
                self.set_colors('default')   
            if self.VarKeyword[i] == 'Variable':
                self.WriteVariable(el, header)
                self.doc.set_sheet_index(0)
                self.set_colors('value')   
                self.doc.set_cell_value(1, i+3, 'link', ('#'+str(el), str(el)))
                self.set_colors('default')   
            if self.VarKeyword[i] == 'Equation':
                self.WriteVariable(el, header)
                self.doc.set_sheet_index(0)
                self.set_colors('value')   
                self.doc.set_cell_value(1, i+3, 'link', ('#'+str(el), str(el)))
                self.set_colors('default')   
        self.doc.set_cell_property('color', 'default')
        self.doc.set_cell_property('background', 'default')

            
            
            
                
        
if __name__=="__main__":
    #myfile.PrintTheWhole()
    #myfile.PrintX()
    #myfile.PrintGamsVariables()
    #myfile.PrintHeader()
##    myfile.WriteTOC()
##    myfile.WriteSet("i", "No")
##    myfile.WriteScalar("f")
##    myfile.WriteParameter("a", "No")
##    myfile.WriteParameter("d")
##    myfile.WriteVariable("x")
##    myfile.WriteVariable("supply")
##    myfile.WriteVariable("cost")
##    myfile.WriteVariable("z")
    #myfile.WriteAll()
    #myfile.SaveOOFile("trnsport.ods")
    
    #myfile.PrintY()
    print "Default options:"
    print default_options
    print "Config file content"
    change_colors(look_costum_config())
    change_settings(look_costum_config())
    print "Costumized options"
    print gdx2oo_options    
    
    dumpfile="trnsport.dump"
    myfile=GdxContent(dumpfile)
    myfile.WriteAll()
    myfile.SaveOOFile("trnsport.ods")


