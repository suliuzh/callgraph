#以影响文件为关键词找到该文件的commit
from git import Repo
import networkx
import logging,re,os,csv,time
import numpy
from diff_parser import parse_diff
from xxx import analyse_xxx
import json
import argparse

class diff_commit(object):
    def __init__(self,path,cm_sha_old,cm_sha_new):
        # self.G = G
        self.cm_sha_old = cm_sha_old
        self.cm_sha_new = cm_sha_new
        self.path = path
        self.changed_apis = {}   #这是更改的numpy模块（粒度为函数或方法）
        self.impact_nodes={}     #影响的模块

        
    def isnotCmt(lines,func_contents):     #判断是否在注释行,
        # multi_lines = []
        begin_line = None
        end_line = 0
        for i,item in enumerate(func_contents):
            #多行注释
            item = item.strip()   #去掉空格符
            if item.startswith("'''") or item.startswith('"""'):
                if begin_line == None:
                    begin_line=i
                else:
                    end_line = i
                    # if begin_line <= lines and lines <= end_line:   #如果在注释行
                    #     return False
                    begin_line = None
        # return True

    def changeget(self,git):
        diff=git.diff(self.cm_sha_new,self.cm_sha_old)
        cm_info=parse_diff(diff)
        files_list=set()
        flag_py = 0
        flag_cm_py = 0
        git.reset('--hard',self.cm_sha_new)  #回到当前版本
        file_apis = []
        for item in cm_info:
            if(item.src_file.endswith('.py')):
                flag_cm_py = 1
                true_path=self.path+'/'+item.src_file
                if os.path.exists(true_path):
                    flag_py = 1
                    files_list.add(true_path)
                    f= open(true_path,'r',encoding='utf-8')
                    contents=f.readlines()
                    file_apis=analyse_xxx([true_path])
                    add_apis_lins=item.hunk_infos['a']
                    if file_apis:
                        for api_lin in add_apis_lins:
                            if file_apis[-1][1]< api_lin:#如果最后一个范围之内，则认为是该API
                                self.changed_apis[file_apis[-1][0]] = true_path
                                continue
                            for i,api in enumerate(file_apis):
                                if api[1] > api_lin:
                                    if (file_apis[i-1])[1]<= api_lin:
                                        # lines = api_lin-(file_apis[i-1])[1]   #距起始行的情况
                                        # func_contents = contents[(file_apis[i-1])[1]:api[1]]   #该函数的内容(之间的内容)
                                        # if isnotCmt(lines,func_contents):
                                        self.changed_apis[file_apis[i-1][0]]=true_path   
                                    else:
                                        break
        file_apis_now = [item[0] for item in file_apis]
        git.reset('--hard',self.cm_sha_old)   #回退上一版本
        for item in cm_info:
            if(item.src_file.endswith('.py')):
                flag_cm_py = 1
                true_path=self.path+'/'+item.src_file
                if os.path.exists(true_path):
                    flag_py = 1
                    files_list.add(true_path)
                    f= open(true_path,'r',encoding='utf-8')
                    contents=f.readlines()
                    file_apis=analyse_xxx([true_path])
                    delete_apis_lins=item.hunk_infos['d']
                    if file_apis:
                        for api_lin in delete_apis_lins:
                            if file_apis[-1][1]< api_lin:#如果最后一个范围之内，则认为是该API
                                self.changed_apis[file_apis[-1][0]] = true_path
                                continue
                            for i,api in enumerate(file_apis):
                                if api[1] == api_lin:
                                    self.changed_apis[api[0]] = true_path  
                                    break
                                elif api[1] > api_lin:
                                    if (file_apis[i-1])[1]< api_lin:
                                        self.changed_apis[file_apis[i-1][0]]=true_path   #前一个才是更改的文件
                                    else:
                                        break
        file_apis_old = [item[0] for item in file_apis]# 之前旧的API
        #通过比较file_api_old file_api_new得到API：增加、删除、更改
        self.len_file = len(files_list)  #文件数量


        self.file_apis = {}
        self.file_apis['file_api_add']=list(set(file_apis_now)-set(file_apis_old))
        self.file_apis['file_api_del']=list(set(file_apis_old)-set(file_apis_now))
        self.file_apis['file_api_chan']=[]
        for api in self.changed_apis:
            if api not in self.file_apis['file_api_add'] and api not in self.file_apis['file_api_del']:
                self.file_apis['file_api_chan'].append(api)
                        
        # # if self.changed_apis == {}:
        # if (flag_cm_py == 0):
        #     print('this commit doesn''t have .py file')
        # elif (flag_py == 0):
        #     print('dont has all .py in the project in the commit')
        # else:
        #     print('no function or method being in this commit')

