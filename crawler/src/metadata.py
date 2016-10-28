import const
import json
import requests
import logging
import os

LOGGING_FILE = 'ipgod.log'
logging.basicConfig(#filename=LOGGING_FILE,
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(filename)s_%(lineno)d  : %(message)s')
logger = logging.getLogger('root')


class Metadata(object):
    
    def getMetaData(dataid):
        """
        Given dataset id, find out all download link
        return all available opendata matadata object
        """
        
        r = requests.get(const.METADATA_URL_PREFIX + dataid)
        x = json.loads(r.text)
        
        if x.get("success") == False:
            return []
        
        Metadata.getLogFile(x)
        
        result = []
        
        for element in x["result"]["distribution"]:
            obj = Metadata(element, x["result"]["organization"], x["result"]["title"])
            result.append(obj)
        
        #result.append(x["result"]["organization"])
        return result
    
    
    def __init__(self, json, organization, title):
        
        self.title = title.replace("/","").rstrip()
        self.organization = organization
        self.resourceID = json.get('resourceID')
        # eg. resourceID = A59000000N-000229-001
        #     datasetID = A59000000N-000229
        self.datasetID = self.resourceID[:-4]
        self.resourceDescription = json.get('resourceDescription')
        self.format = json.get('format',"NA")
        if self.format == "NA":
            logger.warn("No format")
        self.resourceModified = json.get('resourceModified')
    
        # Some data has no downloadURL field
        if 'downloadURL' in json:
            self.downloadURL = json['downloadURL']
            
        self.metadataSourceOfData = json['metadataSourceOfData']
        self.characterSetCode = json['characterSetCode']
        
        
    def getDataID(self):
        return self.dataid
    
    def download(self):
        # TODO: implement resource download logic
        """
        Download data via self.downloadURL field
        return True if download complete, False if download fail
        """
        if not hasattr(self, 'downloadURL'):
            logger.warn(self.resourceID + " NO download URL")
            return False
        else:
            logger.info("download from " + self.downloadURL)
            
            name = self.resourceID.replace("/","")
            dir_name = self.organization+"\\"+self.title
            
            abspath = os.path.abspath(dir_name)+"\\"
            
            
            response = requests.get(self.downloadURL,stream=True)
            
            
            if "zip" in self.downloadURL.lower():
                fileTypeFromURL = "zip"
            elif "csv" in self.downloadURL.lower():
                fileTypeFromURL = "csv"
            elif "xml" in self.downloadURL.lower():
                fileTypeFromURL = "xml"
            elif "txt" in self.downloadURL.lower():
                fileTypeFromURL = "txt"
            else:
                fileTypeFromURL = "NA"     
                
            if "Content-Disposition" in response.headers:
                fileTypeFromContentDesposition = response.headers.get("Content-Disposition")
                fileTypeFromContentDesposition = fileTypeFromContentDesposition[fileTypeFromContentDesposition.rfind(".")+1:len(fileTypeFromContentDesposition)].rstrip("\"")
            else:
                fileTypeFromContentDesposition = "NA"
                
            if "content-type" in response.headers:
                fileTypeFromContentType = response.headers.get("content-type","NA")
                
                if ";" in fileTypeFromContentType:
                    fileTypeFromContentType = fileTypeFromContentType[fileTypeFromContentType.index("/")+1:fileTypeFromContentType.index(";")]
                else:
                    fileTypeFromContentType = fileTypeFromContentType[fileTypeFromContentType.index("/")+1:len(fileTypeFromContentType)]
                    
                if fileTypeFromContentType == "octet-stream" or fileTypeFromContentType == "x-zip":
                    fileTypeFromContentType = "zip"
            else:
                fileTypeFromContentType = "NA"
            
            fileTypeFromFormat = self.format
            
            if fileTypeFromURL != "NA":
                fileType = fileTypeFromURL
            elif fileTypeFromContentDesposition != "NA":
                fileType = fileTypeFromContentDesposition
            elif fileTypeFromContentType != "NA":
                fileType = fileTypeFromContentType
            elif fileTypeFromFormat != "NA":
                fileType = fileTypeFromFormat

            file_name = abspath + name+"." + fileType
            print(file_name)
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024): 
                    if chunk:
                        f.write(chunk)
            
            return True
    
    def getOrganization(self):
        return self.organization
    
    def getDataSetID(self):
        return self.datasetID

    def getResourceID(self):
        return self.resourceID

    def getResourceDescription(self):
        return self.resourceDescription

    def getFormat(self):
        return self.format

    def getResourceModified(self):
        return self.resourceModified

    def getDownloadURL(self):
        return self.downloadURL

    def getMetadataSourceOfData(self):
        return self.metadataSourceOfData

    def getCharacterSetCode(self):
        return self.characterSetCode
    
    def getLogFile(x):
        '''
        This function will create a directory and a log file which under former directory.
        A directory file will be named by the owner name while is the key "organization"'s value in json
        A log file will be named by file title in json
        '''
        # get log file name
        name = x["result"].get("title","NOtitle")
        name = name.replace("/","").rstrip()
        
        # get directory name
        dir_name = x["result"]["organization"].rstrip()
        
        # create a organization directory in current path
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        # create a file title directory under organization directory 
        if not os.path.exists(dir_name+"\\"+name):
            os.makedirs(dir_name+"\\"+name)
        
        # abspath will be the log file's path
        abspath = os.path.abspath(dir_name)+"\\"+name+"\\"
        
        # get log file absolute path
        file_name = abspath + name + ".txt"
        
        # open a file IO stream and write result
        f = open(file_name, "w", encoding = "UTF-8")
        
        for k, v in x["result"].items():
            # print(k,type(v))
            if type(v) is list:
                f.write("%-25s: \n" %(k))
                for j in v:
                    if type(j) is dict:
                        for distribution_key, distribution_value in j.items():
                            f.write("%30s: %s\n"%(distribution_key, distribution_value))
                    else:
                        f.write("%30s\n"%(j))
            else:
                f.write("%-25s: %s\n" %(k,v))
        
