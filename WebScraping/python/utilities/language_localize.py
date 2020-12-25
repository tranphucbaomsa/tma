# Python Code for factory method  
# it comes under the creational  
# Factory Design Pattern 
  
class VietnameseLocalizer: 
    # it simply returns the vietnamese version
    def __init__(self): 
        self.translations = {
            "app_title_start": "------- Quá trình Selenium Web Scraping bắt đầu ---------",
            "app_title_finish": "------- Quá trình Selenium WebScraping kết thúc ---------",
            "enter_path": "Vui lòng nhập đường dẫn sẽ chứa tệp csv (Vd: D:\ExportDocument): ", 
            "please_enter_valid_path":"Vui lòng nhập đường dẫn hợp lệ",
            "please_choose": "Vui lòng chọn: ", 
            "enter_number": "Nhập số: ",
            "choose_nothing":"Bạn chưa chọn gì cả hoặc bạn đã chọn sai",
            "enter_csv_path_first":"Vui lòng nhập đường dẫn sẽ lưu csv trước"
            } 
  
    def localize(self, msg): 
        # change the message using translations
        return self.translations.get(msg, msg) 
  
class EnglishLocalizer: 
    # it simply returns the english version
    def __init__(self): 
        self.translations = {
            "app_title_start": "------- Selenium WebScraping process start ---------",
            "app_title_finish": "------- Selenium WebScraping process finish ---------",
            "enter_path": "Please enter path will contain csv file (Ex: D:\ExportDocument): ", 
            "please_enter_valid_path":"Please enter valid path",
            "please_choose": "Please choose: ", 
            "enter_number":"Enter number: ",
            "choose_nothing":"You choose nothing or you already choose wrong",
            "enter_csv_path_first":"Please enter csv path first"
            }

    # Simply return the same message
    def localize(self, msg): 
        return msg 
  
