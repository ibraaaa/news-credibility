import util.const as const

from sentiwordnet import SentiWordNetCorpusReader

class SentiWordNet(object):
    """ A singleton wrapper class that wraps |SentiWordNetCorpusReader|.
    
        Only the first object of this class creates an instance of |SentiWordNetCorpusReader|  
        which involves reading the sentiwordnet data files, later objects return the previously
        created object.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = SentiWordNetCorpusReader(const.SENTIWORDNET_FILE)
            
        return cls._instance