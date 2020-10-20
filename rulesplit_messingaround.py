import requests #gets urls
import re #regex

def splitRule(rule):
    ...
    #return rulechunks
    pass

rule_url = "https://mikeanders.org/data/CMS/CMS-2018-0101-0001/Rule/CMS-2018-0101-0001.txt"

alltxt = requests.get(rule_url).text.lower()#.encode('unicode_escape').decode() #encodes like raw strings

#Isolate Section 2
initialsplit = alltxt.split("ii. provisions of the proposed regulations") #split before section 2
sec2andon = initialsplit[1] #choose latter half
sec2list = sec2andon.split("iii. collection of information requirements") #split before section 3
splitlist = sec2list[0] #choose first half


rulechunks = {}

startdict = {'a2':['2. proposals for modified participation options under 5-year agreement periods', '3. creating a basic track with glide path to performance-based risk'], \
 'a3':['3. creating a basic track with glide path to performance-based risk', '4. permitting annual participation elections'], \
'a4b':['b. proposals for permitting election of differing levels of risk within the basic track\'s glide path', 'c. proposals for permitting annual election of beneficiary assignment methodology'], \
'a4c':['c. proposals for permitting annual election of beneficiary assignment methodology', '5. determining participation options based on medicare ffs revenue and prior participation '], \
'a5b':['b. differentiating between low revenue acos and high revenue acos', 'c. determining participation options based on prior participation of aco legal entity and aco participants'], \
'a5c':['c. determining participation options based on prior participation of aco legal entity and aco participants', 'd. monitoring for financial performance'], \
'a5d': ['d. monitoring for financial performance', '6. requirements for aco participation in two-sided models'], \
'a6b': ['b. election of msr/mlr by acos', 'c. aco repayment mechanisms'], \
'a6c': ['c. aco repayment mechanisms', 'd. advance notice for and payment consequences of termination '], \
'a6d2': ['(2) proposals for advance notice of voluntary termination', '(3) proposals for payment consequences of termination'], \
'a6d3': ['(3) proposals for payment consequences of termination', '7. participation options for agreement periods beginning in 2019'], \
'a7b': ['b. methodology for determining financial and quality performance for the 6-month performance years during 2019', 'c. applicability of program policies to acos participating in a 6-month performance year'], \
'a7c': ['c. applicability of program policies to acos participating in a 6-month performance year', 'b. fee-for-service benefit enhancements'], \
'b2a': ['a. shared savings program snf 3-day rule waiver', 'b. billing and payment for telehealth services'], \
'b2b': ['b. billing and payment for telehealth services', 'c. providing tools to strengthen beneficiary engagement'], \
'c2': ['2. beneficiary incentives', '3. empowering beneficiary choice'], \
'c3a': ['3. empowering beneficiary choice', 'b. beneficiary opt-in based assignment methodology'], \
'c3b': ['b. beneficiary opt-in based assignment methodology', 'd. benchmarking methodology refinements'],  \
'd2': ['2. risk adjustment methodology for adjusting historical benchmark each performance year', '3. use of regional factors when establishing and resetting acos\' benchmarks'], \
'd3b': ['b. proposals to apply regional expenditures in determining the benchmark for an aco\'s first agreement period', 'c. proposals for modifying the regional adjustment'], \
'd3c': ['c. proposals for modifying the regional adjustment', 'd. proposals for modifying the methodology for calculating growth rates used in establishing, resetting, and updating the benchmark'], \
'd3d': ['d. proposals for modifying the methodology for calculating growth rates used in establishing, resetting, and updating the benchmark', '4. technical changes to incorporate references to benchmark rebasing policies'], \
'd4': ['4. technical changes to incorporate references to benchmark rebasing policies', 'e. updating program policies'], \
'e2': ['2. revisions to policies on voluntary alignment', '3. revisions to the definition of primary care services used in beneficiary assignment'], \
'e3': ['3. revisions to the definition of primary care services used in beneficiary assignment', '4. extreme and uncontrollable circumstances policies for the shared savings program'], \
'e4': ['4. extreme and uncontrollable circumstances policies for the shared savings program', '5. program data and quality measures'], \
'e5':['5. program data and quality measures', '6. promoting interoperability'], \
'e6':['6. promoting interoperability', '7. coordination of pharmacy care for aco beneficiaries'], \
'e7':['7. coordination of pharmacy care for aco beneficiaries', 'f. applicability of proposed policies to track 1+ model acos'], \
'f2':['2. unavailability of application cycles for entry into the track 1+ model in 2019 and 2020', '3. applicability of proposed policies to track 1+ model acos through revised program regulations or revisions to track 1+ model participation agreements'], \
'f3':['3. applicability of proposed policies to track 1+ model acos through revised program regulations or revisions to track 1+ model participation agreements', 'g. summary of proposed timing of applicability']}

for key, value in startdict.items():    
   splitlist = splitlist.split(value[0]) #split on start of desired section
   split_further = splitlist[1].split(value[1]) #split again on start of undesired section
   rulechunks[key] = split_further[0] #choose only first half to upload to dict
   splitlist = splitlist[1] #choose second half to prepare for next split

print(rulechunks.keys())   
#print(rulechunks["f3"])

lengths = [len(chunk) for chunk in rulechunks.values()]
print(lengths) #characters


