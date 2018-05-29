from git import Repo
from datetime import datetime
import re
import os
import json
import yaml
def cvestr(cvemessage):
	cvemessage=list(set(cvemessage))
	result=[]
	if cvemessage.__len__()>0:
		result=cvemessage[0]
	for i in range(1,cvemessage.__len__()-1):
		result+=','
		result+=cvemessage[i]
	return result
def getfiledata(commit,path):
	if commit != None:
		tree=commit.tree
		fnode=tree/path
		return str(fnode.data_stream.read()).replace('\\n','\n').replace('\\t','\t')
	else:
		return None
def getdescription(commit):
	cvemessage=re.findall(r'CVE-\d{4}-\d*',commit.message)
	description = {
	'cve':cvestr(cvemessage),
	'hash': commit.hexsha,
	'summary': commit.summary,
	'description': commit.message,
	'date': str(commit_date),
	'author': commit.author.name
	}
	return description
def save_commit(commit):
	parents=commit.parents
	after=None
	if len(parents)>1:
		sorted_parents = sorted(parents,key=lambda x:x.committed_date)
		after = sorted_parents[-1]
	elif len(parents)==1:
		after=parents[0]
	diffs=commit.diff(after,create_patch=True)
	#print('get '+str(diffs.__len__())+' diffs')
	if diffs.__len__()>config['filter']['maxdiffsnum']:
		print('diffs ignored!')
		return
	diffs_folder_path = os.path.join(diff_root,commit.hexsha)
	if not os.path.exists(diffs_folder_path):
		os.makedirs(diffs_folder_path)
	for diff in diffs:
		#create the diff folder named hexsha
		file_path = diff.b_path if diff.a_path is None else diff.a_path
		#save the diff file
		diff_folder=os.path.join(diffs_folder_path,file_path.replace('/','\\'))
		print(file_path)
		if not os.path.exists(diff_folder):
			os.makedirs(diff_folder)
		if(config['savefile']['diff']):
			with open(os.path.join(diff_folder, 'diff.txt'), 'w') as f:
				f.write(str(diff))
		if(config['savefile']['description']):
			with open(os.path.join(diff_folder, 'description.txt'), 'w') as f:
				f.write(json.dumps(getdescription(commit), indent=4))
		if(config['savefile']['good_file']):
			if(diff.a_path!=None):
				filetype='.'+diff.a_path.split('.')[-1]
				if(filetype.__len__()>4):
					filetype=''
				if(not config['savefile']['keeptype']):
					filetype='.txt'
				with open(os.path.join(diff_folder,'good_file'+filetype),'w') as f:
					filedata=getfiledata(commit,diff.a_path)
					if filedata!=None:
						f.write(filedata)
		if(config['savefile']['bed_file']):
			if(diff.b_path!=None):
				filetype='.'+diff.b_path.split('.')[-1]
				if(filetype.__len__()>4):
					filetype=''
				if(not config['savefile']['keeptype']):
					filetype='.txt'
				with open(os.path.join(diff_folder,'bed_file'+filetype),'w') as f:
					filedata=getfiledata(after,diff.b_path)
					if filedata!=None:
						f.write(filedata)

if __name__=='__main__':
	with open('./config.yml') as f:
		config=yaml.load(f.read())
	repo=Repo(config['path']['repo'])
	diff_root=os.path.expanduser(
		os.path.join(config['path']['output'],'diff'))
	pattern=re.compile(config['keyword'])
	date_from=datetime.strptime(str(config['time']['from']),'%Y-%m-%d')
	date_to=datetime.strptime(str(config['time']['to']),'%Y-%m-%d')
	flag=True
	pagesize=config['pagesize']
	count=0
	while flag:
		commits=list(repo.iter_commits('master',max_count=pagesize,skip=count))
		if(commits.__len__()<pagesize):
			flag=False
		count+=pagesize
		for commit in commits:
			if(re.search(pattern,commit.message)):
				commit_date = commit.committed_datetime.replace(tzinfo=None)
				if((commit_date-date_to).days>0):
					continue
				elif((commit_date-date_from).days<0):
					flag=False
					break
				else:
					print('get commits:'+str(commit.hexsha)+'\n'+str(commit.summary)+'\n'+str(commit_date))
					save_commit(commit)
					print('')	
