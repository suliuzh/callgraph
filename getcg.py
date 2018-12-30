import os,csv,json
from main import mains
import networkx
from  git import Repo
from impact_within import *
import csv

class getcg(object):
    def __init__(self,path,ignore_dirs,cm_sha=''):
        self.path = path
        self.pro_name = path.split('/')[-1]
        self.ignore_dirs = ignore_dirs
        self.cm_sha = cm_sha
        self.used = []
        self.getcg()
    def getcg(self):
        filelist=[]
        walk=os.walk(self.path)
        for root, dirs, files in walk:
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            files = [fn for fn in files if os.path.splitext(fn)[1] == ".py"]
            for file_name in files:
                file_name = os.path.join(root, file_name)
                filelist.append(file_name)
        print(len(filelist))
        self.used=mains(filelist,self.pro_name,self.cm_sha)
    def write_to_graph(self):
        G_numpy_mat=networkx.DiGraph()
        with open('dps/'+self.pro_name+self.cm_sha+'_cg.json','r') as f:
            load_dict = json.load(f)
            for line1,line in load_dict.items():
                for line3 in line:
                    G_numpy_mat.add_node(line1)  #加上文件属性
                    G_numpy_mat.add_node(line3)
                    e=(line1,line3) 
                    G_numpy_mat.add_edge(*e)
        networkx.write_gpickle(G_numpy_mat,'dps/versions/'+self.pro_name+self.cm_sha+'_graph')
        print('---------{},{}------'.format(G_numpy_mat.number_of_nodes(),G_numpy_mat.number_of_edges()))
        os.system('rm dps/'+self.pro_name+self.cm_sha+'_cg.json')  #把中间文件删掉

class diff_graph():
    def __init__(self,G1,G2):
        self.G1 = G1
        self.G2 = G2
        self.diff_gs = 0
    def diff_g(self):
        # if self.G2.number_of_edges == self.G2.number_of_edges:
        #     pass
        # else:
            # #node是否相等
            # Node1 = self.G1.nodes
            # Node2 = self.G2.nodes
            node_weight = 0
            edge_weight = 0

            # #计算入度，调用的情况
            # for node in Node1:
            #     if node not in Node2:
            #         node_weight = node_weight + G1.in_degree(node)
            # for node in Node2:
            #     if node not in Node1:
            #         node_weight = node_weight + G2.in_degree(node)
            for edge in self.G1.edges():
                if edge not in self.G2.edges():
                    edge_weight += 1
            for edge in self.G2.edges():
                if edge not in self.G1.edges():
                    edge_weight += 1
            
            # print(node_weight)
            # print(edge_weight)
            self.diff_gs = edge_weight


#得到不同commit的numpy项目调用图（项目内调用图）
# G_numpy_mat= networkx.read_gpickle('dps/numpy_graph')
ignore_dirs=[]
path='projects/numpy'
name = 'numpy'
repo=Repo(path)
git=repo.git
path = 'projects/numpy'  #这是源代码位置
flag_get = 0 #diff还是获得图
flag_cm = 0 #版本还是commit
if flag_get == 1:
    if flag_cm == 1:
        commits_log=git.log('--oneline','v1.10.2...v1.10.1')  #随便选了版本之间的
        commits = []
        with open('dps/commits/cm.txt','a') as f:
            for item in commits_log.split('\n'):
                cm_sha = item.split()[0]
                commits.append(cm_sha)
                f.write(cm_sha+'\n')
    else:
        with open('dps/versions/versions.txt','r') as f:
            commits = f.readlines()
    for cm in commits:        
        cm_sha = cm.strip('\n')
        try:
            print(cm_sha)
            git.reset('--hard',cm_sha)   #回滚到该版本
            get_cg_class= getcg(path,ignore_dirs,cm_sha)
            get_cg_class.write_to_graph()
        except Exception:
            print('wrong')
else:
    if flag_cm == 1 :
        with open('dps/commits/cm.txt','r') as f:
            commits = f.readlines()
            
    else:
        with open('dps/versions/versions.txt','r') as f:
            commits = f.readlines()
    print(len(commits))
    cm_sha_new = commits[0].strip('\n')
    for i,cm in enumerate(commits):
        cm_sha_old = cm.strip('\n')
        try:
            G1= networkx.read_gpickle('dps/versions/'+name+cm_sha_new+'_graph')
            G2 = networkx.read_gpickle('dps/versions/'+name+cm_sha_old+'_graph')
            print(cm_sha_old,cm_sha_new)
            diff_ = diff_graph(G1,G2)
            diff_.diff_g()
            diff_gs = diff_.diff_gs
            print(diff_gs)
            contents= [cm_sha_old+'-'+cm_sha_new,diff_gs]
            # with open('data/diff.csv','a',newline='') as csv_f:
            #     csv_w = csv.writer(csv_f)
            #     csv_w.writerow(contents)
            #获取本次commit的具体改动
            diff_info = diff_commit(path,cm_sha_old,cm_sha_new)  #当前版本是什么情况
            try:
                diff_info.changeget(git)
                file_apis = diff_info.file_apis
                print('file_api_add:',len(file_apis['file_api_add']))
                print('file_api_del:',len(file_apis['file_api_del']))
                print('file_api_chan:',len(file_apis['file_api_chan']))
                contents= [cm_sha_old+'-'+cm_sha_new,diff_gs,len(file_apis['file_api_add']),len(file_apis['file_api_del']),len(file_apis['file_api_chan'])]
                with open('data/diff_cm_vers.csv','a',newline='') as csv_f:
                    csv_w = csv.writer(csv_f)
                    csv_w.writerow(contents)
            except Exception:
                print('wrong')
        except Exception:
            pass
        cm_sha_new = cm_sha_old

