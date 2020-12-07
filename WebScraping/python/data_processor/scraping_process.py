# super class 
class DataScraping: 
     
     # protected data members 
     _url = None
     _roll = None
     _branch = None
     
     # constructor 
     def __init__(self, url, roll, branch):   
          self._url = url 
          self._roll = roll 
          self._branch = branch 
     
     # protected member function    
     def _displayRollAndBranch(self): 
          # accessing protected data members 
          print("Roll: ", self._roll) 
          print("Branch: ", self._branch) 
  
  
# derived class 
class ScrapingNonSelenium(DataScraping): 
  
       # constructor  
       def __init__(self, url, roll, branch):  
                DataScraping.__init__(self, url, roll, branch)  
          
       # public member function  
       def displayDetails(self): 
                 # accessing protected data members of super class  
                print("Name: ", self._name)  
                 # accessing protected member functions of super class  
                self._displayRollAndBranch() 

# derived class 
class ScrapingSelenium(DataScraping): 
  
       # constructor  
       def __init__(self, name, roll, branch):  
                DataScraping.__init__(self, name, roll, branch)  
          
       # public member function  
       def displayDetails(self): 
                    
                 # accessing protected data members of super class  
                print("Name: ", self._name)  
                    
                 # accessing protected member functions of super class  
                self._displayRollAndBranch() 