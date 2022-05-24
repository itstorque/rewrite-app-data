from importlib.resources import path
import time

import subprocess
from construct import Path2
import psutil

import glob

import plistlib

from difflib import SequenceMatcher

class AppPath:
    
    def __init__(self, path1, path2) -> None:
        self.path1 = str(path1)
        self.path2 = str(path2)
        
    def __str__(self) -> str:
        return self.path2
    
    def __repr__(self):
       return self.__str__()
   
    def loc(self):
       return self.path1 + "/" + self.path2

class App:

    def __init__(self, app_path) -> None:
        
        self.app_path = app_path
        
        self.app_name = self.normalize_string( app_path.split("/")[-1].split(".app")[0] )

        # subprocess.call(
        #     ["/usr/bin/open", "-a", app_path]
        # )
        
        print(self.app_name)
        
        print(set( i.name() for i in psutil.process_iter() if "h" in i.name()))
        
        self.process = list(i for i in psutil.process_iter() if SequenceMatcher(None, i.name().lower(), self.app_name).ratio() > 0.8)[0]
        
        print("Launched", self.process, "with pid", self.get_pid())
        
        time.sleep(1)
        
        print(self.get_active_containers())
        
    def get_pid(self):
        return self.process.pid
    
    def pid_lsof(self):
        
        output = str(subprocess.check_output(
            ["lsof", "-p", str(self.get_pid())]
        ))
        
        output = output.split("\\n")
        
        output = ['/'+'/'.join(i.split("/")[1:]) for i in output]
        
        return output
        
    def get_active_containers(self):
        
        parent_dir = "/Library/Containers"
        
        containers = set( 
                            i .split(parent_dir) [0] + 
                            parent_dir + '/' +
                            i .split(parent_dir) [1] [1:]
                              .split('/')[0] 
                            for i in self.pid_lsof() 
                            if parent_dir in i 
        )
        
        return containers

    def list_plists(self):

        paths = self.get_active_containers()

        return [AppPath(path, i.split(path)[1])
                for path in paths
                for i in glob.glob(path + '/**/*.plist', recursive=True) 
                ]

    def important_plists(self):
        return self.importance_sort(self.list_plists())

    def importance_sort(self, array, app_name=None, penalize_dots=False, enable_keywords=False):
        
        key_func_kwargs = {'app_name': app_name, 'penalize_dots': penalize_dots, 'enable_keywords': enable_keywords}
            
        # Calling str(x) causes the Path object to give the second arg!
        key_func = lambda x: self.importance_distance(str(x), **key_func_kwargs)
    
        return sorted(
            array,
            key = key_func,
            reverse=True
        )

    def importance_distance(self, test, app_name=None, penalize_dots=False, enable_keywords=False):
        
        test = self.normalize_string(test)
        
        distractions = {"apple", "google", "analytics", "security", "facebook", "sdk", "firebase", "fb"}
        keywords = {"data", "player", "coins", "money", "currency", "stats", "level", "items", "food", "pet"} if enable_keywords else set()
        
        ratio = SequenceMatcher(None, self.app_name, test).ratio() * (1 if app_name==None else app_name)
        
        if self.app_name.lower() in test.lower() and app_name==None:
            ratio += 100
        
        for i in distractions:
            if i not in self.app_name:
                ratio -= SequenceMatcher(None, i, test.lower()).ratio()**2/len(distractions)
                
                if i in test: ratio -= 10
        
        for i in keywords:
            if i not in self.app_name:
                ratio += SequenceMatcher(None, i, test.lower()).ratio()**2/len(keywords)
                
                if i in test: ratio += 10
                
        if penalize_dots and "." in test: ratio -= 1
                
        # print(test, ratio)
        
        return ratio
    
    def normalize_string(self, string):
        
        string = string.lower()
        
        illegal_chars = [" ", "/"]
        
        for i in illegal_chars:
            string = string.replace(i, "")
        
        return string
    
    def read_plist(self, app_path, choice=None):
        
        with open(app_path.loc(), 'rb') as fp:
            
            pl = plistlib.load(fp)
            
            if choice == None:
                print(self.importance_sort(pl.keys(), app_name=-1, penalize_dots=True, enable_keywords=True))
                
            else:
                print(pl[choice])


if __name__=="__main__":

    # app = App("/Applications/Adorable Home.app")
    app = App("/Users/torque/Applications/Hades.app")

    # path = app.get_path()

    # print(app.important_plists())
    
    app.read_plist(app.list_plists()[0])
    
    choice = "playerData_1"
    
    app.read_plist(app.list_plists()[0], choice)