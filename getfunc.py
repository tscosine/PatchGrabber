import re
import os
import yaml

def getName(function):
	return re.split(r'\(|;',function)[0]
def getFuncionName(folderpath):
	pattern=re.compile(r'(?:static )?(?:inline )?(?:unsigned)?\w+ \*?\w+')
	diffstr=open(os.path.join(folderpath,'diff.txt')).read()
	function=re.split(r'@@ ',diffstr)
	functionname=[]
	for f in function:
		name = getName(f)
		if(re.match(pattern,name) and not re.search(r'struct',name)):
			functionname.append(getName(f))
	functionname=list(set(functionname))#remove the same name
	return functionname
def findFunctionEnd(begin,str):
	i=begin
	count=0
	while i<str.__len__():
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
	with open(os.path.join(folderpath,name+'.txt'),'w') as f:
		f.write(func)
def islegal(path):
	afile=False
	bfile=False
	diff=False
	for root,dirs,files in os.walk(path):
		for f in files:
			if(f=='a_file.c'):
				afile=True
			if(f=='b_file.c'):
				bfile=True
			if(re.split('\.',f)[0]=='diff'):
				diff=True
	return (afile and bfile and diff)
def getTargetFolder(path):
	result=[]
	for f in os.listdir(config['path']['output']):
		path1=os.path.join(config['path']['output'],f)
		for path2 in os.listdir(path1):
			r=os.path.join(path1,path2)
			if(islegal(r)):
				result.append(r)
	return result
if __name__=='__main__':
	# testfile=open('/home/cosine/Desktop/filename.txt','a')
	with open('./config.yml') as f:
		config=yaml.load(f.read())
	targetfolder=getTargetFolder(config['path']['output'])
	for tar in targetfolder:
		functionname=getFuncionName(tar)
		# for name in functionname:
		# 	testfile.write('$'+str(name)+'\n')
		a_func=getFunctionBody(functionname,'a_file.c',tar)
		b_func=getFunctionBody(functionname,'b_file.c',tar)
		for i in range(functionname.__len__()):
			saveAsFile('a_'+re.split(r' ',functionname[i])[-1],a_func[i],tar)
			saveAsFile('b_'+re.split(r' ',functionname[i])[-1],b_func[i],tar)
	print('Done.')