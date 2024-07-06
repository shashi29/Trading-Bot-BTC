from config import Config
from scanner import StockScanner
from utils.excel_writer import ExcelWriter

def main():
    config = Config()
    scanner = StockScanner(config)
    results = scanner.scan()
    
    excel_writer = ExcelWriter()
    for ticker, data in results.items():
        excel_writer.write(ticker, data)

if __name__ == "__main__":
    main()