# We can then import these at begin
# import ViewOperation class in presentation_layer\client_app.py
from presentation_layer.client_app import ViewOperation

def main():
    viewOperation = ViewOperation.getInstance()
    viewOperation.web_scraping_main()

if __name__ == "__main__":
    main()