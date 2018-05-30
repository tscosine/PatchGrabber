import re
import os
import yaml
def getFuncionName(folderpath):
	pattern=re.compile(r'(?:static )?(?:inline )?(?:unsigned)?\w+ \*?\w+')
	diffstr=open(os.path.join(folderpath,'diff.txt')).read()
	function=re.split(r'@@',diffstr)
	functionname=[]
	for f in function:
		name = re.split(r'\(|;',f)[0]
		name = name[re.search(r'\w',name).span()[0]:]
		if(re.match(pattern,name) and not re.search(r'struct',name)):
			functionname.append(name)
	functionname=list(set(functionname))#remove the same name
	return functionname
def findFunctionEnd(begin,str):
	i=begin
	count=0
	if str.__len__()<=begin or begin<0:
		return begin
	while i < str.__len__():
		if(str[i]=='{'):
			count+=1
		elif(str[i]=='}'):
			count-=1
			if(count<=0):
				return i+1
		i+=1
	return begin
def getFunctionBody(functionname,filename,folderpath):
	filestr=open(os.path.join(folderpath,filename)).read()
	result=[]
	for name in functionname:
		begin=filestr.find(name)
		end=findFunctionEnd(begin,filestr)
		result.append(filestr[begin:end])
	return result
def saveAsFile(name,func,folderpath):
	with open(os.path.join(folderpath,name+'.c'),'w') as f:
		f.write(func)
def islegal(path):
	afile=False
	bfile=False
	diff=False
	for root,dirs,files in os.walk(path):
		for f in files:
			if(f=='good_file.c'):
				afile=True
			if(f=='bad_file.c'):
				bfile=True
			if(re.split('\.',f)[0]=='diff'):
				diff=True
	return (afile and bfile and diff)
def getTargetFolder(path):
#get all diff path from root path
	result=[]
	repopath=os.path.join(config['path']['output'],'diff')
	for f in os.listdir(repopath):
		path1=os.path.join(repopath,f)
		for path2 in os.listdir(path1):
			r=os.path.join(path1,path2)
			if(islegal(r)):
				result.append(r)
	return result
if __name__=='__main__':
	# testfile=open('/home/cosine/Desktop/filename.txt','a')
	with open('./config.yml') as f:
		config=yaml.load(f.read())
	difffolder=getTargetFolder(os.path.join(config['path']['output'],'diff'))
	goodFunctionFolder=os.path.join(config['path']['output'],'goodfunction')
	badFunctionFolder=os.path.join(config['path']['output'],'badfunction')
	if not os.path.exists(goodFunctionFolder):
		os.mkdir(goodFunctionFolder)
	if not os.path.exists(badFunctionFolder):
		os.mkdir(badFunctionFolder)
	for folder in difffolder:
		print('serach folder:'+str(folder))
		functionname=getFuncionName(folder)
		print('getfunction name:')
		for f in functionname:
			print(f)
		# for name in functionname:
		# 	testfile.write('$'+str(name)+'\n')
		good_func=getFunctionBody(functionname,'good_file.c',folder)
		bad_func=getFunctionBody(functionname,'bad_file.c',folder)
		for i in range(functionname.__len__()):
			saveAsFile(re.split(r' ',functionname[i])[-1],
				good_func[i],goodFunctionFolder)
			saveAsFile(re.split(r' ',functionname[i])[-1],
				bad_func[i],badFunctionFolder)
	print('Done.')
