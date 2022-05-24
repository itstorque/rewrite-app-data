from difflib import SequenceMatcher
from faulthandler import enable
import glob
import plistlib

class App:

    def __init__(self, appname) -> None:
        self.appname = self.normalize_string(appname)

    def get_path(self):
        # TODO
        return "/Users/torque/Library/Containers/B01AF5EB-B588-485C-A383-FEFFF76D0CF5"

    def list_plists(self):

        path = self.get_path()

        return [i.split(path)[1] for i in glob.glob(path + '/**/*.plist', recursive=True)]

    def important_plists(self):
        return self.importance_sort(self.list_plists())

    def importance_sort(self, array, app_name=None, penalize_dots=False, enable_keywords=False):
    
        return sorted(
            array,
            key = lambda x: self.importance_distance(x, app_name=app_name, penalize_dots=penalize_dots, enable_keywords=enable_keywords),
            reverse=True
        )

    def importance_distance(self, test, app_name=None, penalize_dots=False, enable_keywords=False):
        
        test = self.normalize_string(test)
        
        distractions = {"apple", "google", "analytics", "security", "facebook", "sdk", "firebase"}
        keywords = {"data", "player", "coins", "money", "currency", "stats", "level"} if enable_keywords else set()
        
        ratio = SequenceMatcher(None, self.appname, test).ratio() * (1 if app_name==None else app_name)
        
        if self.appname.lower() in test.lower() and app_name==None:
            ratio += 100
        
        for i in distractions:
            if i not in self.appname:
                ratio -= SequenceMatcher(None, i, test.lower()).ratio()**2/len(distractions)
                
                if i in test: ratio -= 10
        
        for i in keywords:
            if i not in self.appname:
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
    
    def read_plist(self, rel_loc):
        with open(self.get_path() + rel_loc, 'rb') as fp:
            pl = plistlib.load(fp)
            print(self.importance_sort(pl.keys(), app_name=-1, penalize_dots=True, enable_keywords=True))
                
        


def ls():
    return []

def print_plist():
    return

def edit_plist():
    return

def find_plists():
    return


if __name__=="__main__":

    app = App("Adorable Home")

    path = app.get_path()

    print(app.important_plists())
    
    app.read_plist(app.list_plists()[0])