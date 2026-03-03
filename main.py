from scrapper import scrape_jobs
from analysis import analyze_jobs

if __name__ == "__main__":
    df = scrape_jobs(max_pages=10)
    analyze_jobs()
