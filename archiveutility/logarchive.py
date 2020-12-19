# Python Program to archive logs from a SAS configuration directory: sasgnn March 2016
# Change Log
# April 4, sasgnn, added the ability to exclude directories 

import os, fnmatch, datetime, time, shutil, inspect, socket, sys, zipfile
 
#function finds all log files under a directory including sub-directories

def find_files(directory, pattern):
   
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

# get python version and os
version=int(str(sys.version_info[0])+str(sys.version_info[1]))
curos=os.name

print("Python Version is: "+ str(version))
print("Operating System: "+ str(curos))

#parameters read from a properties file 

# get the path for the script file this is where the properties file will bbe
thepath=os.path.split(inspect.getsourcefile(lambda:0))
install_dir=thepath[0]
prop_file=os.path.join(install_dir, "archive.properties")

print("Properties read from: " +prop_file)

#create a dictionary with the lines from the properties file
#read only lines that start with a character

myparams=dict(line.strip().split('=') for line in open(prop_file) if line[0].isalpha())
 
print("Parameters are:")
print(myparams)

# set parameters
numdays=int(float(myparams['numdays']))
execmode=int(float(myparams['execmode']))
delete=int(float(myparams['delete']))
debug=int(float(myparams['debug']))
logs_loc=myparams['logs_loc']
archive_loc=myparams['archive_loc']
logf=os.path.join(install_dir,"archive.log")
excluded=myparams['excluded']
exdirs=excluded.split(',')

now=time.time()

# open log file to write messages
logfile=open(logf,'w')

# write different messages if running in execmode mode
if execmode:
   logfile.write("Log opened session in execute mode: " + time.ctime(now) + "\n")
   logfile.write("Log files WILL be archived to: " + archive_loc + "\n")
   print("Running in execute mode logs will be archived at: " +archive_loc)
else:
   logfile.write("Log opened session in non execute mode: " + time.ctime(now) + "\n")
   logfile.write("Log files WOULD be archived to: " + archive_loc + "\n")
   print("Running in no-execute mode view " +logf + " to see what would be archived")
       

# walk thru the files and copy them to the archive location

#create a directory with a name of the timestamp only if running in execmodeute mode

newdirname=time.ctime(now)

#strip unsupported charachter names for windows
newdirname=newdirname.replace(' ','')
newdirname=newdirname.replace(':','')

#get the hostname
host=socket.gethostname()

archivepath=os.path.join(archive_loc, host + newdirname )

if execmode >=1:

    if os.path.isdir(archive_loc)==False: os.makedirs(archive_loc)

    # only needed for file copy rather than archive
    #if os.path.isdir(archivepath)==False: os.makedirs(archivepath)

    zfilename=archivepath+".zip";
    zf=zipfile.ZipFile(zfilename,"w",zipfile.ZIP_DEFLATED,allowZip64=True);

# for all the logs found copy then to the archive location
for filename in find_files(logs_loc, '*.log'):

     
    # try to get the modified time, catch errors, if no errors continue
    try:
        filetime=os.path.getmtime(filename)
    except OSError, e:
        print e.args
    else:
        shortname=os.path.basename(filename)
        thedir=os.path.dirname(filename)

        # only archive fi directory not excluded
        if thedir not in exdirs:
           
            # copy if  date is older than number of days
            if  filetime < (now-(numdays*86400)):
            
                if debug: print ('Archived:'+filename+' Date:'+time.ctime(filetime))
           
                logfile.write(filename + " " + time.ctime(filetime) + "\n")
                
                if execmode>=1:
                                                                            
                    #copy files to archive and optionally delete        
                    #shutil.copy2(filename,os.path.join(archivepath,shortname))

                    #add to zip file instead of copy
                    zf.write(filename)            
                                      
                    if delete:
                        try: os.remove(filename)
                        except OSError as e:
                            print("Cannot delete file" + filename)
                            logfile.write("Cannot delete "+filename+ "\n")
                                                

if execmode >=1: zf.close()

print ("Processing complete check log at "+logf);

logfile.write("Processing complete at " + time.ctime(now))

logfile.close()
