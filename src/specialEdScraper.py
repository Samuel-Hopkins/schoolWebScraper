import mechanize
import ssl
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import lxml
import re


print("Begining scraping job.")
timestamp = datetime.now().date().isoformat()
pattern = re.compile(r".*Staff Directory*")

csv_filename = "output_specialEd.csv"
with open(csv_filename, "w") as csv_f:  # Open the file in write mode only once
    print("Generating output file: " + csv_filename)
    writer = csv.writer(csv_f, delimiter="\t")
    writer.writerow(["Service", "Email", "Name", "Title", "Date"])  # Write the header

ssl._create_default_https_context = ssl._create_unverified_context
br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [
    (
        "User-agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
    )
]
response = br.open(
    "https://www2.montgomeryschoolsmd.org/departments/special-education/programs-services/"
)

content = response.read()
soup = BeautifulSoup(content, "lxml")

services_left = soup.find("div", class_="twocol floatl")
services_right = soup.find("div", class_="twocol floatr")
left_links = services_left.find_all("a")
right_links = services_right.find_all("a")
all_links = left_links + right_links
standard_links = []
special_links = []
for link in all_links:
    if "HIAT" in str(link):
        hiat_link = link["href"]
    elif "Infants" in str(link):
        infant_link = link["href"]
    else:
        standard_links.append(link["href"])

standard_directory_links = []
print("getting standard directory links")
for link in standard_links:
    try:
        service_page = br.open(link).read()
    except:
        print("failure following link: " + link["href"])
    service_page_soup = BeautifulSoup(service_page, "lxml")
    staff_directory_link = service_page_soup.find("a", string="Staff Directory")
    if staff_directory_link == None:
        staff_directory_links = service_page_soup.find_all("a", string=pattern)
        for link in staff_directory_links:
            if "montgomeryschoolsmd" in link["href"]:
                staff_directory_link = link
                break
    if staff_directory_link == None:
        staff_directory_link = service_page_soup.find("a", string="Team Members")
    standard_directory_links.append(staff_directory_link["href"])

print("Scraping Standard Webpages")
standard_directory_links = set(standard_directory_links)  # remove duplicates
for link in standard_directory_links:
    try:
        staff_directory_page = br.open(link).read()
    except:
        print("failure following link: " + link)

    staff_directory_soup = BeautifulSoup(staff_directory_page, "lxml")
    dept_info = staff_directory_soup.find("div", id="dept-info")
    service_name = dept_info.find("h2").text.strip()
    print("scraping service: " + service_name)
    staff_info = staff_directory_soup.find("div", id="searchwrapes").find("div")
    staff_members = staff_info.find_all("ul")
    for staff_member in staff_members:
        staff_member_info = staff_member.find("li")
        name = staff_member_info.find("h2").find("span").text
        title_and_email = staff_member_info.find_all("p")
        title = title_and_email[0].text
        email = title_and_email[2].find("a").text
        with open(csv_filename, "a") as csv_f:  # Open the file in append mode
            writer = csv.writer(csv_f, delimiter="\t")
            writer.writerow([service_name, email, name, title, timestamp])

# print("Scraping non-Standard Webpages")
# try:
#     hiat_page = br.open(hiat_link).read()
# except:
#     print("failure scraping link: " + hiat_link)


print("Scraping job finished.")
