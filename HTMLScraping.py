import requests
from bs4 import BeautifulSoup
import time
from _datetime import datetime

# Using Beautiful Soup and requests, scraping the main page and getting total number of pages
f = open("LandisData_Sample.txt","w",encoding="utf-8")
numpages = 0
Owner_list = []
url = "https://www.assessor.shelby.tn.us/PropertySearch.aspx?StreetNumber=&StreetName=&FirstName=S&LastName=&ParcelID=&Business=&IR_Request=off&PageSize=100"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")
try:
    for i in soup.find_all("span"):
        spanid = i.get("id")
        if (i.get("id") == "PageNavigator1_spnPages"):
            numpages = int(i.get_text())
            break
except Exception as e:
    print(e)

# Going to each page, getting Parcel ID for each and getting required information
for pagecntr in range(1,numpages):
    url = "https://www.assessor.shelby.tn.us/PropertySearch.aspx?StreetNumber=&StreetName=&FirstName=S&LastName=&ParcelID=&Business=&IR_Request=off&PageSize=100"
    parameters = {
        "Page" : pagecntr
    }
    contresp = requests.get(url,params=parameters)

    soup = BeautifulSoup(contresp.text,"html.parser")
    idlist = []
    try:
        recordcounter = 0
        for i in soup.find_all("td"):
            TupleData_dict = {
                "FloorArea": "",
                "Property Address": "",
                "OwnerName": "",
                "OwnerAddress": "",
                "Date of Sale": "",
                "Sales Price": ""
            }
            if(i.get("width") == "110"):
                personIDformatted = i.get_text()

# Scraping the floor area information from the Product record page for that particular ID
                proprecordurl = "https://www.assessor.shelby.tn.us/PropertySearchDetail2017.aspx?id=" + personIDformatted +"&ReturnUrl=https%3a%2f%2fwww.assessor.shelby.tn.us%2fPropertySearch.aspx%3fStreetNumber%3d%26StreetName%3d%26FirstName%3dS%26LastName%3d%26ParcelID%3d%26Business%3d%26IR_Request%3doff%26PageSize%3d100&IR_Request=off"
                proprecordresp = requests.get(proprecordurl)

                proprecordsoup = BeautifulSoup(proprecordresp.text,"html.parser")
                for j in proprecordsoup.find_all("span"):
                    if(j.get("id") == "spnLandAcres"):
                        TupleData_dict["FloorArea"] = j.get_text()
                        break

# Scraping the required information from the Sales record page for that particular ID
                salesdataurl = "https://www.assessor.shelby.tn.us/PropertySearchSales.aspx?id=" + personIDformatted + "&ReturnUrl=https%3a%2f%2fwww.assessor.shelby.tn.us%2fPropertySearch.aspx%3fStreetNumber%3d%26StreetName%3d%26FirstName%3dS%26LastName%3d%26ParcelID%3d%26Business%3d%26IR_Request%3doff%26PageSize%3d100&IR_Request=off"
                salesdataresp = requests.get(salesdataurl)

                salesdatasoup = BeautifulSoup(salesdataresp.text,"html.parser")
                for j in salesdatasoup.find_all("span"):
                    if (j.get("id") == "spnAddress"):
                        TupleData_dict["Property Address"] = j.get_text()
                    elif (j.get("id") == "spnOwnerName"):
                        TupleData_dict["OwnerName"] = j.get_text()
                    elif(j.get("id") == "spnOwnerAddress"):
                        TupleData_dict["OwnerAddress"] = j.get_text()
                        break

                for j in salesdatasoup.find_all("tr"):
                    try:
                        if(j.get("class")[0] == "PropertySearchDetail-ItemStyle"):
                            tdlist = j.find_all("td")
                            TupleData_dict["Date of Sale"] = tdlist[0].get_text()
                            TupleData_dict["Sales Price"] = tdlist[1].get_text()
                            break
                    except:
                        continue
                recordcounter += 1
                print(recordcounter, end=".", flush=True)
            else:
                continue
            Owner_list.append(TupleData_dict)
    except Exception as e:
        print(e)
        break
    print("Page added")
    time.sleep(1)

print(Owner_list)

# Creating list of owners and date of sales, prices to find flippers.
Sales_dict = {}
Price_dict = {}

for i in range(0,len(Owner_list)):
    Oname_key = Owner_list[i]["OwnerName"]
    Sales_dict[Oname_key] = []

for i in range(0,len(Owner_list)):
    Oname_key = Owner_list[i]["OwnerName"]
    Sales_dict[Oname_key].append(Owner_list[i]["Date of Sale"])

# After sorting the date, if the last two sales for that owner occurred within a year, its a flipper.
for i in Sales_dict:
    sorted(Sales_dict[i],reverse=True)

print(Sales_dict)

FlipperList = []

for i in Sales_dict:
    try:
        d1: datetime = datetime.strptime(Sales_dict[i][0], "%m/%d/%Y")
        d2 = datetime.strptime(Sales_dict[i][1], "%m/%d/%Y")
        if((d1-d2).days < 365):
            FlipperList.append(i)
    except:
        continue

print(FlipperList)
Flippers = ",".join(FlipperList)
f.write(Flippers + "\n\n")

for i in range(0,len(Owner_list)):
    Oname_key = Owner_list[i]["OwnerName"]
    Price_dict[Oname_key] = []

for i in range(0,len(Owner_list)):
    Oname_key = Owner_list[i]["OwnerName"]
    Price_dict[Oname_key].append(Owner_list[i]["Sales Price"])

# Printing flipper and Prices of the properties sold for further analysis
for i in Price_dict:
    if(i in FlipperList):
        Prices = " ".join(Price_dict[i])
        f.write(i + " : " + Prices + "\n")

f.close()





