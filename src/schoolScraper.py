import mechanize
import ssl
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import lxml


def school_scrape(links):
    for link in links:
        school_page = br.follow_link(url=link["href"]).read()
        school_page_soup = BeautifulSoup(school_page, "lxml")
        dept_info = school_page_soup.find("div", id="dept-info")
        school_name = dept_info.find("h2").text.strip()
        print("scraping school: " + school_name)
        staff_info = school_page_soup.find("div", id="ContentPlaceHolder1_pnlStructure")
        staff_sections = staff_info.find_all("div", recursive=False)
        for section in staff_sections:
            staff_members = section.find_all("ul")
            for staff_member in staff_members:
                staff_member_info = staff_member.find("li")
                name = staff_member_info.find("h2").find("span").text
                title_and_email = staff_member_info.find_all("p")
                title = title_and_email[0].text
                email = title_and_email[1].find("a").text
                with open(csv_filename, "a") as csv_f:  # Open the file in append mode
                    writer = csv.writer(csv_f, delimiter="\t")
                    writer.writerow(
                        [school_name, email, name, title, school_level, timestamp]
                    )
        br.back()


print("Begining scraping job.")
timestamp = datetime.now().date().isoformat()

csv_filename = "output.csv"
with open(csv_filename, "w") as csv_f:  # Open the file in write mode only once
    print("Generating output file: " + csv_filename)
    writer = csv.writer(csv_f, delimiter="\t")
    writer.writerow(
        ["School Name", "Email", "Name", "Title", "School Level", "Timestamp"]
    )  # Write the header

ssl._create_default_https_context = ssl._create_unverified_context
br = mechanize.Browser()
br.set_handle_robots(False)
response = br.open("https://ww2.montgomeryschoolsmd.org/directory/schools.aspx")

content = response.read()
soup = BeautifulSoup(content, "lxml")

schools = soup.find("div", class_="tab-content card")
school_levels = schools.select("div[class*=tab-pane][class*=fade]")
for level in school_levels:
    school_links = level.find_all("a")
    school_level = level.find("h3").text.strip()
    print("SCRAPING SCHOOL LEVEL: " + school_level)
    school_scrape(school_links)

print("Scraping job finished.")
