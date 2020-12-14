# import ScrapingNonSelenium and ScrapingSelenium class
# defined in business_processor\scraping_process.py
from business_processor.scraping_process import ScrapingNonSelenium, ScrapingSelenium

"""
-----// begin private member function: can access within the class only //-----
"""
# show input choice to user (1,2,3,...)
def __let_user_pick(options):
    print("Please choose:")
    for idx, element in enumerate(options):
        print("{}) {}".format(idx+1,element))
    i = input("Enter number: ")
    try:
        if 0 < int(i) <= len(options):
            return int(i)
    except:
        pass
    return None

# show input path that store csv to user 
def __let_user_input_path():
    path = input("Please enter path will contain csv file (Ex: D:\ExportDocument):   ")
    try:
        if path:
            return path
    except:
        pass
    return None
"""
-----// end private member function: can access within the class only //-----
"""

def main():
    print('-------WebScraping process start.---------')
    print('\n')

    csv_path = __let_user_input_path() # returns string (Ex: D:\ExportDocument)

    if csv_path != None:
        options = ["Scraping Without Selenium.", "Scraping With Selenium."]
        choice = __let_user_pick(options) # returns integer

        if choice == 1:
            sns = ScrapingNonSelenium(csv_path)
            sns.scrapWebsite()
        elif choice == 2:
            ss = ScrapingSelenium(csv_path)
            ss.scrapWebsite()
        else:
            print('You choose nothing')
    else:
         print('Please enter csv path first')

    print('\n')
    print('-------WebScraping process finish.---------')

if __name__ == "__main__":
    main()
