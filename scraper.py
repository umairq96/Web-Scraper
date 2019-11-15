import json
from bs4 import BeautifulSoup as soup
import requests

page_url = (
    "http://ca.healthinspections.us/napa/search.cfm?start=1&1=1&sd=01/01/1970&ed=03/01/2017&kw1=&kw2=&kw3="
    "&rel1=N.permitName&rel2=N.permitName&rel3=N.permitName&zc=&dtRng=YES&pre=similar"
)


def main():

    # Create beautiful soup object
    source = requests.get(page_url).text
    page_soup = soup(source, 'lxml')

    # Get all the urls to the individual inspections
    local_urls = []
    for link in page_soup.findAll('a'):
        anchor = link.attrs["href"]

        if anchor.startswith('../_templates/'):
            local_urls.append(anchor)

    count = 0
    facility = {}

    # Going through each individual inspection link
    for i in local_urls:
        seperate = i.split(" ")
        real_url = "http://ca.healthinspections.us" + seperate[0].lstrip('..') + '%20' + seperate[1]

        facility_source = requests.get(real_url).text
        facility_soup = soup(facility_source, 'lxml')

        text = facility_soup.find('div', class_='topSection')
        info = text.text.split('\n')

        count += 1
        print("Facility " + str(count) + " Information: ")

        facility_name = info[2].strip().lstrip("Facility Name:")
        print("Facility Name: " + facility_name)

        street = info[6].strip().lstrip("Address: ")
        print("Street: " + street)

        city_split = info[7].split(',')
        city = city_split[0].strip()
        print("City: " + city)

        state_split = city_split[1].split(' ')
        state = state_split[1].strip()
        print("State: " + state)

        zip = state_split[2].strip()
        print("Zip: " + zip)

        inspection_date = info[4].strip().lstrip("Date: ")
        print("Inspection Date: " + inspection_date)

        inspection_type = info[12].strip().lstrip("Inspection Type: ")
        print("Inspection Type: " + inspection_type)

        page2 = facility_soup.find('div', class_='page2Content')
        grade_section = page2.find_all('td', {'class': 'center bold'})
        grade = grade_section[1].text.strip()
        print("Inspection Grade: " + grade)

        # find the inside table to get out of compliance violations
        inside_table = facility_soup.find_all('table', {'class': 'insideTable'})
        violations = []
        for j in inside_table:
            text = j.find_all('tr')

            # find all the image tags in the "out" column
            for k in range(1, len(text), 1):
                compliance = text[k].find_all('td')
                images = compliance[2].find_all('img')

                # find all "out" that are checked
                for image in images:
                    if image['src'] == 'http://ca.healthinspections.us/webadmin/dhd_135/paper/images/box_checked_10x10.gif':
                        out_of_compliance = compliance[0].text
                        violations.append(out_of_compliance)
                        print("Out of Compliance Violation: " + out_of_compliance)

        print()

        # Storing information in JSON structure
        facility[facility_name] = {
            'Facility Name': facility_name,
            'Facility Street': street,
            'Facility City': city,
            'Facility State': state,
            'Facility Zip': zip,
            'Inspection Date': inspection_date,
            'Inspection Type': inspection_type,
            'Inspection Grade': grade,
            'Out of Compliance': violations,
        }

    s = json.dumps(facility)

    with open("D:\\data.txt", 'w') as f:
        f.write(s)


if __name__ == '__main__':
    main()
