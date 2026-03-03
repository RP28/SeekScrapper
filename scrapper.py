import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def scrape_jobs(search_query="python developer", location="Sydney NSW", max_pages=10, output_csv="seek_jobs.csv"):
    """Scrape SEEK for a given query and location, with pagination.

    Returns a pandas DataFrame containing the results and writes to `output_csv`.
    """
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    url = f"https://www.seek.com.au/{search_query.replace(' ', '-')}-jobs/in-{location.replace(' ', '-')}"

    jobs = []
    seen_ids = set()
    page_count = 0

    current_url = url
    while page_count < max_pages:
        page_count += 1
        print(f"Loading page {page_count}: {current_url}")

        driver.get(current_url)
        time.sleep(4)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.find_all("article")

        if not job_cards:
            print(f"No jobs found on page {page_count}, stopping")
            break

        print(f"Found {len(job_cards)} job cards on page {page_count}")

        for job in job_cards:
            job_id = job.get("data-job-id")
            if job_id:
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

            title = job.get("aria-label", "").strip()

            link = None
            link_tag = job.find("a", {"data-automation": "job-list-item-link-overlay"})
            if not link_tag:
                link_tag = job.find("a", {"data-automation": "job-list-view-job-link"})
            if link_tag and link_tag.has_attr("href"):
                href = link_tag["href"]
                link = href if href.startswith("http") else "https://www.seek.com.au" + href

            company = ""
            company_tag = job.find("a", {"data-automation": "jobCompany"})
            if company_tag:
                company = company_tag.text.strip()

            loc = ""
            loc_tag = job.find("span", {"data-automation": "jobCardLocation"})
            if loc_tag:
                loc = loc_tag.get_text(strip=True)
            else:
                loc_tag = job.find("a", {"data-automation": "jobLocation"})
                if loc_tag:
                    loc = loc_tag.text.strip()

            date = ""
            for txt in job.stripped_strings:
                if txt.lower().startswith("listed") or "ago" in txt.lower():
                    date = txt
                    break

            # additional fields
            short_desc = ""
            desc_tag = job.find("span", {"data-automation": "jobShortDescription"})
            if desc_tag:
                short_desc = desc_tag.text.strip()

            sub_class = ""
            sub_tag = job.find("span", {"data-automation": "jobSubClassification"})
            if sub_tag:
                sub_class = sub_tag.text.strip()

            classification = ""
            class_tag = job.find("span", {"data-automation": "jobClassification"})
            if class_tag:
                classification = class_tag.text.strip()

            work_arrange = ""
            wa_tag = job.find(attrs={"data-testid": "work-arrangement"})
            if wa_tag:
                work_arrange = wa_tag.text.strip()

            job_type = ""
            for txt in job.stripped_strings:
                if "full time" in txt.lower() or "part time" in txt.lower():
                    job_type = txt.strip()
                    break

            jobs.append({
                "Title": title,
                "Company": company,
                "Location": loc,
                "Date Posted": date,
                "Link": link,
                "Short Description": short_desc,
                "Sub Classification": sub_class,
                "Classification": classification,
                "Work Arrangement": work_arrange,
                "Job Type": job_type
            })

        next_tag = soup.find("a", {"aria-label": "Next"})
        if not next_tag or not next_tag.get("href"):
            print("No more pages found, stopping")
            break

        href = next_tag["href"]
        current_url = href if href.startswith("http") else "https://www.seek.com.au" + href
        time.sleep(2)

    df = pd.DataFrame(jobs)
    df.to_csv(output_csv, index=False)

    print(f"Scraped {len(jobs)} jobs successfully across {page_count} pages!")
    driver.quit()
    return df


if __name__ == "__main__":
    scrape_jobs()
