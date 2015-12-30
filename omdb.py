"""
>>> import requests
>>> r = requests.get('https://github.com/timeline.json')
>>> r.json()


    r = requests.get('http://www.omdbapi.com/?t=Batman&page=1&r=xml')
    print dir(r)
    print r.text

"""

from requests import get as rget
from openpyxl import load_workbook
from openpyxl import Workbook

_VERBOSE=True
_DOIT=True

OMDBdir = '/home/godzilla/Desktop/OMDBpy'
irvXLS = '%s/dvd-list.xlsx'%OMDBdir
infoXLS= '%s/dvd-info.xlsx'%OMDBdir
backXLS = '%s/dvd-info-bak.xlsx'%OMDBdir
badF = '%s/bad-movie-names.txt'%OMDBdir

keyL = [u'Title', u'Year', u'Series / Episode / ID', u'B-R',
        u'Runtime', u'DLed', u'Director', u'Actors', u'tomatoMeter',
        u'imdbRating', u'Plot', u'tomatoConsensus', u'Genre',
        u'Website', u'Awards', u'Language', u'Country', u'BoxOffice', u'Type']

TYPE='movie'   # default search mode

def make_not_found(movieN):
    theD = {field: ''  for field in keyL}
    theD[u'Title']= '%s'%movieN
    return theD

def _getData(movieN, yr, seid, type):
    # need to add in epise=, season=, y= etc
    reqStr = '?r=json&tomatoes=true&type=%s'%(type or TYPE.lower())
    if yr: reqStr = reqStr+'&year=%s'%yr
    #seid='%s'%seid
    if not seid:
        reqStr=reqStr+'&t=%s'%movieN
    elif seid.startswith('tt'):
        reqStr = reqStr+'&i=%s'%seid
    else:
        # parse the string
        x = seid.split('E')
        theS = x[0][1:]
        if len(x) == 1:
            theE = None
        elif len(x)==2:
            theE = x[1]

        reqStr=reqStr+'&t=%s'%movieN
        if theS: reqStr = reqStr+'&season=%s'%theS
        if theE: reqStr = reqStr+'&episode=%s'%theE
            
    if _VERBOSE: print reqStr
    if _DOIT:
        r = rget('http://www.omdbapi.com/'+reqStr)
        res=r.json()
    else:
        res = make_not_found(movieN)
        res['Response']=True
    return res

def _splitName(movieN, part=1):
    left = movieN.find('[')
    if left==-1:
        leftN = movieN
        rightN = None
    else:
        leftN, rightN = movieN.split('[')
        rightN=rightN.strip()[:-1]

    if part==0: return leftN
    if part==1: return rightN
    if part==2: return (leftN, rightN)

def _joinNames(leftN, rightN):
    name= '%s '%leftN
    if rightN: name=name+' [%s]'%rightN
    return name

def _getSearchName(movieN):
    searchN = _splitName(movieN) or movieN
    return _normalizeSearchN(searchN)

def _normalizeSearchN(movieN):
    if type(movieN) is type(3):
        movieN = '%s'%movieN
    elif movieN.lower().endswith(' a'):
         movieN='A '+movieN[:-1]
    elif movieN.lower().endswith(' the'):
        movieN='The '+movieN[:-3]
    movieN=movieN.strip()
    if movieN[-1]==',': movieN=movieN[:-1]
    return movieN

def _alphabetizeTitle(titleN):
    movieN,searchN = _splitName(titleN, part=2)
    movieN=movieN.strip()
    if movieN[-1]==',': movieN=movieN[:-1]
    if movieN.startswith('A '):
        movieN=movieN[2:]+', A'
    elif movieN.startswith('The '):
        movieN=movieN[4:]+', The'
    return _joinNames( movieN, searchN )

def getData(movieL, ws, badFP):

    # TODO: search name and listing name may differ!!! grab name in ()
    
    movieN, yr, seid, br, run, dled = movieL[0:6]
    _type = movieL[-1]

    if dled=='x':                   # we have the data already, doanatouch
        res = movieL
        if False:
            res[0]=_alphabetizeTitle( movieN )
            
    elif movieN.startswith('%%'):   # placeholder
        res=make_not_found(movieN)
        # switch modes
        TYPE=movieN[2:]
    else:                           # we need to get data
        searchN = _getSearchName(movieN)
        print 'getting info for %s ...'%searchN
        res=_getData(searchN, yr, seid, _type)
        # check for {"Response":"False","Error":"Movie not found!"}
        if res['Response'] == "False":
            print 'not found!!!'
            badFP.write(movieN.encode('utf8')+'\n')
            res=make_not_found(movieN)
            res['DLed']=''
        else:
            res['DLed']='x'

        # TODO: fix the following so we use newfound name as appropriate 
        res[u'Title']=_alphabetizeTitle( movieN )
        res[u'Series / Episode / ID'] = seid
        res[u'B-R'] = br

    if type(res) is type({}):
        res=[res[key]  for key in keyL] 
        
    ws.append(res)

def getDiscLold():
    wb = load_workbook(filename=irvXLS, read_only=True)
    ws = wb['Sheet1'] # ws is now an IterableWorksheet

    titleL=[]
    for row in ws.rows:
        valL = [ row[i].value for i in range(4)]
        valL.append('')
        titleL.append( valL )

    return titleL

def getDiscL(save):
    wb = load_workbook(filename=infoXLS, read_only=False)
    ws = wb['AllInfo'] # ws is now an IterableWorksheet

    titleL=[]
    for row in ws.rows:
        valL = [ row[i].value for i in range(len(keyL))]
        titleL.append( valL )
    
    if save: wb.save(backXLS)
    return titleL

def main(save=False):
    
    titleL = getDiscL(save)
    
    wb = Workbook()
    ws=wb.active
    ws.title='AllInfo'
    ws.append(keyL)
    badFP = open(badF, 'w')
    
    for title in titleL[1:]:
        getData(title, ws, badFP)
        
    if save: wb.save(infoXLS)
    badFP.close()

def __match():
    import re
    SEIDre= re.compile('^S\d+E\S+')
    seidL = ('S1', 'S1E1', 'S1E#1.2') 
    for seid in seidL:
        print SEIDre.match(seid)
    

if __name__ == '__main__':

    main(save=True)
