# import ScrapingNonSelenium and ScrapingSelenium class
# defined in business_processor\scraping_process.py
from business_processor.scraping_process import ScrapingNonSelenium, ScrapingSelenium

# import EnumStatusCode class
# defined in utilities\app_enum.py
from utilities.app_enum import EnumMainOptions

# import EnglishLocalizer and VietnameseLocalizer class
# defined in utilities\language_localize.py
from utilities.language_localize import EnglishLocalizer, VietnameseLocalizer

"""
-----// begin private member function: can access within the class only //-----
"""
# show input choice to user (1,2,3,...)
def __let_user_pick(options, vi):
    print(vi.localize("please_choose"))
    for idx, element in enumerate(options):
        print("{}) {}".format(idx+1,element))
    i = input(vi.localize("enter_number"))
    try:
        if 0 < int(i) <= len(options):
            return int(i)
    except:
        pass
    return None

# show input path that store csv to user 
def __let_user_input_path(vi):
    path = input(vi.localize("enter_path"))
    try:
        if path:
            return path
    except:
        pass
    return None

# message will be translate to multi language
def __LanguageTranslation(language="en"): 
    """Factory Method"""
    localizers = { 
        "vi": VietnameseLocalizer, 
        "en": EnglishLocalizer
    } 
  
    return localizers[language]() 
"""
-----// end private member function: can access within the class only //-----
"""

def main():
    vi = __LanguageTranslation("vi")

    print('-------WebScraping process start.---------')
    print('\n')

    csv_path = __let_user_input_path(vi) # returns string (Ex: D:\ExportDocument)

    if csv_path != None:
        # tmp_code: options = ["Scraping Without Selenium.", "Scraping With Selenium."]
        # convert the enum object [EnumMainOptions] to a list [options]
        options = [name for name in dir(EnumMainOptions) if not name.startswith('_')]
        choice = __let_user_pick(options, vi) # returns integer

        if choice == 1:
            sns = ScrapingNonSelenium(csv_path)
            sns.scrapWebsite()
        elif choice == 2:
            ss = ScrapingSelenium(csv_path)
            ss.scrapWebsite()
        else:
            print(vi.localize("choose_nothing"))
    else:
         print(vi.localize("enter_csv_path_first"))

    print('\n')
    print('-------WebScraping process finish.---------')

if __name__ == "__main__":
    main()
