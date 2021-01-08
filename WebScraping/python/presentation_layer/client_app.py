from business_layer import *
from utils import *

import sys

class ViewOperation:
    __instance = None

    @staticmethod 
    def getInstance():
      # Static access method.
      if ViewOperation.__instance == None:
         ViewOperation()
      return ViewOperation.__instance

    def __init__(self):  # init method or constructor   
        # Virtually private constructor.
        if ViewOperation.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ViewOperation.__instance = self

    """
    -----// begin private member function: can access within the class only //-----
    """
    # show input choice to user (1,2,3,...)
    def __let_user_pick(self, options, en):
        print(en.localize("please_choose"))
        for idx, element in enumerate(options):
            print("{}) {}".format(idx+1,element))
        i = input(en.localize("enter_number"))
        try:
            if 0 < int(i) <= len(options):
                return int(i)
        except:
            pass
        return None

    # show input path that store csv to user 
    def __let_user_input_path(self, en):
        path = input(en.localize("enter_path"))
        try:
            if path:
                return path
        except:
            pass
        return None

    # message will be translate to multi language
    def __LanguageTranslation(self, language="en"): 
        """Factory Method"""
        localizers = { 
            "vi": VietnameseLocalizer, 
            "en": EnglishLocalizer
        } 
    
        return localizers[language]() 
    """
    -----// end private member function: can access within the class only //-----
    """

    """
    -----// begin public member function: easily accessible from any part of the program //-----
    """
    def web_scraping_main(self):
        en = self.__LanguageTranslation()
        pathLibOperation  = PathLibOperation.getInstance()

        print(en.localize("app_title_start"))
        print('\n')

        csv_path = self.__let_user_input_path(en) # returns string (Ex: D:\ExportDocument)

        if csv_path != None:
            isValid = pathLibOperation.check_valid_dir_names(csv_path)

            if isValid:
                # tmp_code: options = ["Scraping Without Selenium.", "Scraping With Selenium."]
                # convert the enum object [EnumMainOptions] to a list [options]
                options = [name for name in dir(EnumBrowserOptions) if not name.startswith('_')]
                choice = self.__let_user_pick(options, en) # returns integer

                if choice == 1:
                    sns = ScrapingChromeSelenium(csv_path)
                    sns.scrapWebsite()
                elif choice == 2:
                    ss = ScrapingFirefoxSelenium(csv_path)
                    ss.scrapWebsite()
                else:
                    print(en.localize("choose_nothing"))
            else:
                print(en.localize("please_enter_valid_path"))
        else:
            print(en.localize("enter_csv_path_first"))

        print('\n')
        print(en.localize("app_title_finish"))
        sys.exit(101) # exit a Python Program that doesn’t involve throwing an exception
    """
    -----// end public member function: easily accessible from any part of the program //-----
    """