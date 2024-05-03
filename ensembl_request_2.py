"""Extracting mutation information from ensembl with ensembl rest api"""

# Import modules
import requests
import json
import re
import time

# TODO: Integrate new functions with the main program
# Test hgvs coding tests and extra print statements are included in the "ensembl_request_with_prints.py" file.

# Takes the list of hgvs_coding if it contains more than 200 items and splits it into smaller lists.
# Integrated into get_hgvs_genomic function
def split_list(list, size):
    """
    Splits the list into smaller lists.
    """
    # TODO: Cleanup comments
    
    # Return a list of lists
    
    # size = This is the number of items you want each sublist (chunk) to contain.
    # range(0, len(list), size):  This generates a sequence of numbers starting from 0 up to the length of the list, incrementing by size each time. 
    #  - Each number in this sequence represents the starting index of a new chunk in the original list.
    
    # list[i:i + size]: This slices the list from index i to i + size
    
    # Loop execution:
    # - The list comprehension iterates over each i generated by the range function.
    # - For each i, it slices the list from i to i + size and appends the slice to the new list.
    # - Each sublist is then added to the outer list that the list comprehension is building.
    return [list[i:i + size] for i in range(0, len(list), size)] 

# Takes a list of HGVS coding, url to ensembl,and Ensembl REST API (variant_recorder) 
# headers as input and returns a dictionary with the corresponding HGVS genomic (HGVSG) notation.
def get_hgvs_genomic(hgvs_input, url, headers):
    """
    Extracts and HGVS genomic (HGVSG) corresponding to the input HGVS coding (HGVSC).
    """
    # TODO: Integrate split_list function
    # TODO: Start with if statement if the list is larger than 200.
    
    # Ensembl REST API (variant_recorder)
    data = json.dumps({"ids": hgvs_input})                               # JSON data for the POST request 
    response = requests.post(url, headers=headers, data=data)            # Send a POST request
    
    # Storage
    hgvs_genomic = {}
    hgvs_failed = [(i, hgvs) for i, hgvs in enumerate(hgvs_input)]       # A list of tuples (index, value)
    processed = set()                                                    # A set to keep track of processed items
    
    # Proceed with successful requests
    if response.status_code == 200:                                      # Status code 200 means successfull request                         
        
        result = response.json()                                         # Parse the response JSON
        found_match = False                                              # Flag for matching HGVS coding
        
        # Iterate over each HGVS coding
        for allele in result:                       
            for _, variant_data in allele.items():                       # Iterate over each dictionary in the list
                if type(variant_data) == dict:                           # Errors saved as lists, hits saved as dictionaries.
                    
                    # Iterate through each HGVS input to match with responses
                    for j, hgvs in enumerate(hgvs_input):                             # List of HGVS coding
                        
                        if hgvs in processed:                                         # If this hgvs has been processed before, skip it
                            continue
                            
                        base_hgvs_coding = hgvs.split(':')[0].split('.')[0]           # Remove version number
                        
                        # Check if result contains both HGVSC and HGVSG
                        if 'hgvsc' in variant_data and 'hgvsg' in variant_data:                        
                            
                            # Save genomic data and remove the input from the failed list
                            if any(base_hgvs_coding in s.split(':')[0].split('.')[0] for s in variant_data['hgvsc']): # Check if the input HGVS coding matches any returned HGVSC values (ignoring version)
                                hgvs_genomic[hgvs] = variant_data['hgvsg'][0]            # Save the genomic data
                                hgvs_failed.remove((j, hgvs))                            # Remove the tuple (index, value)                          # Remove successfull input from failed list
                                processed.add(hgvs)                                      # Add this hgvs to the set of processed items
                                
                                found_match = True                                       # Flag for matching HGVS coding
                                
                else:
                    print("Input contains errors.")
                    
        for _, hgvs in hgvs_failed:
            print(f"Failed to match: {hgvs}")
        
        if not found_match:
            print("No matching HGVS coding found.")
    
    # Print error status code and message if the request failed
    else:
        print(f"Failed to retrieve data: {response.status_code}\n")
        print(f"{response.text}\n")
        
    return hgvs_genomic, hgvs_failed


# TODO: nest the output in dictionaries instead?
#Converts the genomic HGVS notation to chromosome and locus information
def hgvs_converter(hgvs_genomic):
    """ 
    Takes the HGVS dictionary as input and returns mutation information in for VCF creation.
    Uses the regular expression module.
    """
    
    chr_info = {}
    pattern = re.compile(r'(\d{2})\..*\.(\d+)[ATCGU]')      # Patterns for chromosome number and locus
    
    # Save chromosome and locus information
    for key, genomic in hgvs_genomic.items():
        match = pattern.search(genomic)
        
        if match:
            # Check if the chromosome is somatic, X or Y
            if match.group(1) == "23":
                chromosome = "X"
            elif match.group(1) == "24":
                chromosome = "Y"
            else:
                chromosome = match.group(1).lstrip("0")    # lstrip() removes the potential "0" from the first position.
                
            locus = match.group(2)
            chr_info[key] = (chromosome, locus)
        else:
            print(f"No match found in: {genomic}")
            
    return chr_info


#### Test program ####
if __name__ == "__main__":
    
    # REST API URL and headers
    url = "https://rest.ensembl.org/variant_recoder/homo_sapiens"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    
    # test hgvs coding inputs
    hgvs_notation = ["ENST00000169551:c.609G>A", "ENST00000558353:c.323G>A", "ENST00000519026:c.1396G>A", "ENST00000431539:c.757C>T"]   # 1 working 2 not 3 working 4 not
    #hgvs_notation = ["ENST00000603986:c.1050C>T", "ENST00000603986:c.1223G>A", "ENST00000383070:c.55C>T", "ENST00000383070:c.217G>A"] # X and Y
    #hgvs_notation = ["ENST00000603986:c.1050C>T", "ENST00000383070:c.55C>T"] # X and Y
    
    # TODO: Here, add an if statement with argument if input is more than 200
    # TODO: In main program, use "n" args in the if
    
    # Call HGVS genomic function (genomic in dict, failed in list)
    hgvs_genomic_test, hgvs_failed_test = get_hgvs_genomic(hgvs_notation, url, headers)
    
    # Test print of the program
    print("\nMatching coding-genomic:\n")
    
    # Print the successful HGVS coding
    for key, value in hgvs_genomic_test.items():
        print(f"coding: {key}, genomic: {value}")
        
    print("\nHere starts the failed:\n")
    
    # Print the failed HGVS coding
    for failed in hgvs_failed_test:
        print(f"Failed: {failed}")
    
    
    # Call the HGVS converter function
    chr_info = hgvs_converter(hgvs_genomic_test)
    
    # Test prints for the chromosome information
    print("\nHere starts the chromosome information:\n")
    
    for key, value in chr_info.items():
        print(f"key: {key}\nvalue: {value}")