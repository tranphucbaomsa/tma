# We can then import these at begin
from presentation_layer import *

def main():
    v_op = ViewOperation.getInstance()
    v_op.web_scraping_main()
    # mySqlStoringData = MySqlStoringData.getInstance()
    # mySqlStoringData.read_imdb("")

if __name__ == "__main__":
    main()