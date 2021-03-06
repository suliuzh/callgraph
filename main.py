#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,json
import logging
from glob import glob
from optparse import OptionParser  # TODO: migrate to argparse

from analyzer import CallGraphVisitor
from node import Flavor

def mains(filelist,pro_name,cm_sha):
    used={}
    used_def={}
    analyzer_ast= CallGraphVisitor(filelist)
    for n in analyzer_ast.uses_edges:
            for n2 in analyzer_ast.uses_edges[n]:
                # if n.flavor not in (Flavor.UNKNOWN,Flavor.UNSPECIFIED) and n2.flavor not in (Flavor.UNKNOWN,Flavor.UNSPECIFIED): 
                if n.flavor in (Flavor.CLASSMETHOD,Flavor.FUNCTION,Flavor.METHOD,Flavor.CLASS) and n2.flavor not in (Flavor.UNKNOWN,Flavor.UNSPECIFIED,Flavor.NAME,Flavor.NAMESPACE):
                    used_def[n.get_name()] = {'namespace':n.namespace,'name':n.name,'flavor':repr(n.flavor)}
                    used_def[n2.get_name()] = {'namespace':n2.namespace,'name':n2.name,'flavor':repr(n2.flavor)}
                    if n.get_name() not in used.keys():
                        used[n.get_name()]=[]
                        used[n.get_name()].append(n2.get_name())
                    else:
                        used[n.get_name()].append(n2.get_name())

    json_str = json.dumps(used)   #转成字符串
    used_dict = json.loads(json_str)   #转成字典
    with open('dps/'+pro_name+cm_sha+'_cg.json','w') as f:
            json.dump(used_dict,f,indent=4) 
    
    # json_str = json.dumps(used_def)   #转成字符串
    # useddef_dict = json.loads(json_str)   #转成字典
    # with open('dps/'+pro_name+cm_sha+'.json','w') as f:
    #         json.dump(useddef_dict,f,indent=4)
    # used={}
    # used_def={}    
    # for n in analyzer_ast.cross_edge:
    #     for n2 in analyzer_ast.cross_edge[n]:
    #         used_def[n.get_name()] = {'namespace':n.namespace,'name':n.name,'flavor':repr(n.flavor)}
    #         used_def[n2.get_name()] = {'namespace':n2.namespace,'name':n2.name,'flavor':repr(n2.flavor)}
    #         if n.get_name() not in used.keys():
    #             used[n.get_name()]=[]
    #             used[n.get_name()].append(n2.get_name())
    #         else:
    #             used[n.get_name()].append(n2.get_name())
    # json_str = json.dumps(used)   #转成字符串
    # used_dict = json.loads(json_str)   #转成字典
    # with open('dps/'+pro_name+'_numpy_cg.json','w') as f:
    #         json.dump(used_dict,f,indent=4) 
    
    # json_str = json.dumps(used_def)   #转成字符串
    # useddef_dict = json.loads(json_str)   #转成字典
    # with open('dps/'+pro_name+'_numpy.json','w') as f:
    #         json.dump(useddef_dict,f,indent=4)
       
    return None    

