#!/usr/bin/env python3

""" Module to test papers.py  """

__author__ = "Darius Chow and Ryan Prance, Adopted from: Susan Sim"
__email__ = "darius.chow@mail.utoronto.ca, ryan.prance@mail.utoronto.ca, ses@drsusansim.org"
__copyright__ = "Adopted from: 2015 Susan Sim"
__license__ = "MIT License"

__status__ = "Exercise"

# imports one per line
import pytest
import os
import json
import re
from exercise2 import decide

DIR = "test_jsons/"
os.chdir(DIR)

'''
countries:
dictionary mapping country codes (lowercase strings) to dictionaries
containing the following keys:
"code","name","visitor_visa_required",
"transit_visa_required","medical_advisory"
'''
COUNTRIES_FILE = "countries.json"
COUNTRIES = None
with open(COUNTRIES_FILE, "r") as countries_file:
    countries_content = countries_file.read()
    COUNTRIES = json.loads(countries_content)

REQUIRED_FIELDS = ("first_name", "last_name", "birth_date", "passport", "home", "from", "entry_reason")
LOCATION_FIELDS = ("home", "from", "via")
REQUIRED_FIELDS_LOCATION = ("city", "region", "country")
REASON_FOR_ENTRY = ('returning', 'visiting')

def test_returning():
    """
    Travellers are returning to KAN.
    """
    assert decide("test_returning_citizen.json", COUNTRIES_FILE) ==\
        ["Accept", "Accept", "Quarantine"]

def test_decide_no_citizens_file():
    """
    Ensure that the file contains zero returning citizens.
    """
    with open("test_decide_no_citizens.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)
    assert len(citizen_json) == 0

def test_decide_no_citizens():
    """
    No travellers are returning.
    """
    assert decide("test_decide_no_citizens.json", COUNTRIES_FILE) == []

def test_decide_missing_required_information_file():
    """
    Ensure that the file contains citizens with missing information fields.
    """
    with open("test_decide_missing_required_information.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)

    for person in citizen_json:
        required_fields_included = True
        for item in REQUIRED_FIELDS:
            if item not in person:
                required_fields_included = False
            else:
                if item in LOCATION_FIELDS:
                    if not valid_location_field(person[item]):
                        required_fields_included = False
                elif item is "passport":
                    assert valid_passport_or_visa(person[item])
        assert required_fields_included == False

def test_decide_missing_required_information():
    """
    Travellers have required information that is missing, including incomplete location information.
    """
    assert decide("test_decide_missing_required_information.json", COUNTRIES_FILE) == ["Reject"] * 16

def test_decide_unknown_locations_file():
    """
    Ensure that the file contains travellers that have locations listed that are unknown.
    """
    with open("test_decide_unknown_locations.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)

    assert valid_file_contents(citizen_json)

    for person in citizen_json:
        unknown_location_found = False
        for item in person:
            if item in LOCATION_FIELDS:
                if valid_country_code(person[item]['country'], COUNTRIES) == False:
                    unknown_location_found = True
        assert unknown_location_found

def test_decide_unknown_locations():
    """
    Travellers have locations listed that are unknown. Assuming no missing required fields and no missing fields from
    locations.
    """
    assert decide("test_decide_unknown_locations.json", COUNTRIES_FILE) == ["Reject"] * 5

def test_decide_KAN_citizens_file():
    with open("test_decide_KAN_citizens.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)

    assert valid_file_contents(citizen_json)
    for person in citizen_json:
        for item in person:
            location_fields_to_check = LOCATION_FIELDS[1:]  # Excludes home location field of country_code KAN
            if item in location_fields_to_check:
                country_code = person[item]['country']
                assert COUNTRIES[country_code]['medical_advisory'] == ""

def test_decide_KAN_citizens():
    """
    Travellers that have their home location as KAN. These travellers did not travel from or through a country with
    a medical advisory and all required information is present.
    """
    assert decide("test_decide_KAN_citizens.json", COUNTRIES_FILE) == ["Accept"] * 3

def test_decide_visitors_require_visas_valid_visas():
    """
    Visitors that have their home location other than KAN (but still a valid location), and because of their home
    countries, they require a visa to enter. Their visas are valid. These travellers did not travel from or through
    a country with a medical advisory and all required information is present.
    """
    assert decide("test_decide_visitors_require_visas_valid_visas.json", COUNTRIES_FILE) == ["Accept"] * 1

def test_decide_visitors_require_visas_invalid_visas():
    """
    Visitors that have their home location other than KAN (but still a valid location), and because of their home
    countries, they require a visa to enter. Their visas are invalid/expired because they are older than 2 years.
    These travellers did not travel from or through a country with a medical advisory and all required information
    is present.
    """
    assert decide("test_decide_visitors_require_visas_invalid_visas.json", COUNTRIES_FILE) == ["Accept"] * 1

def test_decide_visitors_visas_not_needed():
    """
    Visitors that have their home location other than KAN (but still a valid location), but because of their home
    countries, they do not require a visa to enter. These travellers did not travel from or through a country with
    a medical advisory and all required information is present.
    """
    assert decide("test_decide_visitors_visas_not_needed.json", COUNTRIES_FILE) == ["Accept"] * 1

def test_decide_KAN_citizens_via_country_with_medical_advisory():
    """
    Testing for KAN citizens that travelled from or via a country with a medical advisory. All required information
    is present.
    """
    assert decide("test_decide_KAN_citizens_via_country_with_medical_advisory.json", COUNTRIES_FILE) ==\
           ["Quarantine"] * 1

def test_decide_visitors_via_country_with_medical_advisory():
    """
    Testing for visitors that are approved thus far (nothings missing, everything is valid, visa is present if
    required), but travelled from or via a country with a medical advisory. All required information is present.
    """
    assert decide("test_decide_visitors_via_country_with_medical_advisory.json", COUNTRIES_FILE) ==\
           ["Quarantine"] * 1

#####################
# HELPER FUNCTIONS ##
#####################

def valid_location_field(location):
    """
    Finds out if a location field (in the form of a dictionary) is a validly filled out and returns a boolean.

    :param location: a dictionary
    :return: True if the dictionary has all of and only the location fields. False otherwise.
    """
    valid = True
    if len(location) != 3:
        valid = False
    else:
        for item in REQUIRED_FIELDS_LOCATION:
            if item not in location:
                valid = False
    return valid

def test_valid_location_field():
    d1 = {'city': 'city_name', 'region': 'region_name', 'country':'country_name'}
    assert valid_location_field(d1)
    d2 = {'city': 'city_name', 'country':'country_name', 'region': 'region_name'}
    assert valid_location_field(d2)
    d3 = {'city': 'city_name', 'province': 'province_name', 'country':'country_name'}
    assert valid_location_field(d3) == False
    d4 = {'municipality': 'municipality_name', 'state': 'state_name', 'country':'country_name'}
    assert valid_location_field(d4) == False
    d5 = {'city': 'city_name', 'country':'country_name'}
    assert valid_location_field(d5) == False
    d6 = {'city': 'city_name', 'region': 'region_name', 'province': 'province_name', 'country':'country_name'}
    assert valid_location_field(d6) == False

def valid_country_code(location_code, countries):
    """
    Finds out if a country code in a location field is valid by comparing to a valid country codes list,
    and returns a boolean.

    :param location_code: a dictionary with "country" as a key, denoting the country code
    :param countries: a dictionary of countries, with the key representing the country code
    :return: True if the location's country code is contained in the valid list of country codes. False otherwise.
    """
    country_match = False
    for country_code in countries.keys():
        if location_code == country_code:
            country_match = True
    return country_match

def test_valid_country_code():
    countries = {
        "ALB": {
            "code": "ALB",
            "name": "Duchy of Alberdore",
            "visitor_visa_required": "0",
            "transit_visa_required": "0",
            "medical_advisory": ""
        },
        "BRD": {
            "code": "BRD",
            "name": "Eminent Plutarchy of Vemenin",
            "visitor_visa_required": "1",
            "transit_visa_required": "1",
            "medical_advisory": ""
        }
    }
    assert valid_country_code("ALB",countries)
    assert valid_country_code("MLC",countries) == False

def valid_passport_or_visa(passport_or_visa_number):
    """
    This function checks to see if a passport or visa number is valid, as defined by having five groups of
    alphanumeric characters (case-insensitive), separated by dashes.

    :param passport_or_visa_number: string that represents a passport or visa number
    :return: True, if the string conforms to the regular expression, False otherwise.
    """
    valid_regex = re.compile(r'^([\dA-Za-z]{5}-){4}[\dA-Za-z]{5}$')
    valid_regex_match = valid_regex.search(passport_or_visa_number)
    valid = True
    if valid_regex_match is None:
        valid = False
    return valid

def test_valid_passport_or_visa():
    s1 = "6P294-42HR2-95PSF-93NFF-2TEWF"
    assert valid_passport_or_visa(s1)
    s2 = "TJq2R-25stx-Fyc52-02rm0-420DS"
    assert valid_passport_or_visa(s2)
    s3 = "33T0R-8T3T2-W_C77-243GE-42O_D"
    assert valid_passport_or_visa(s3) == False
    s4 = "T2EW5-WT255-019RW-2RWS4-42FFX-TNX2R"
    assert valid_passport_or_visa(s4) == False

def valid_date(date):
    """
    This function checks to see if date is valid, as defined by YYYY-MM-DD.
    This function only assumes that the month can range from 01 to 12, and day can range from 01 to 31.

    :param date: a string representing a birthdate
    :return: True, if the birth_date conforms to the format with correct values (see above assumptions), False otherwise
    """
    valid_regex = re.compile(r'^\d{4}-(\d{2})-(\d{2})$')
    valid_regex_match = valid_regex.search(date)
    valid = True
    if valid_regex_match is None:
        valid = False
    else:
        try:
            month = int(valid_regex_match.group(1))
            day = int(valid_regex_match.group(2))
            if 12 < month or month < 1 or 31 < day or day < 1:
                valid = False
        except:
            valid = False
    return valid

def test_valid_date():
    assert valid_date("1952-12-25")
    assert valid_date("2002-01-05")
    assert valid_date("195-12-25") == False
    assert valid_date("1952-13-05") == False
    assert valid_date("1982-02-32") == False
    assert valid_date("1972-3-9") == False

def valid_file_contents(file_contents):
    """
    This function checks to see that the file contents are valid: no required fields are missing, location
    information is complete, birth_date and passport/visa number is valid.

    :param file_contents: a list of dictionaries denoting returning citizens
    :return: True if the file contents are valid, False otherwise
    """
    valid_file = True
    for person in file_contents:
        for item in REQUIRED_FIELDS:
            if item not in person:
                valid_file = False
        for item in person:
            if item in LOCATION_FIELDS:
                if not valid_location_field(person[item]):
                    valid_file = False
            elif item is "passport":
                if not valid_passport_or_visa(person[item]):
                    valid_file = False
            elif item is "visa":
                if not valid_passport_or_visa(person[item]['code']) or not valid_date(person[item]['date']):
                    valid_file = False
            elif item is "entry_reason":
                if person[item] not in REASON_FOR_ENTRY:
                    valid_file = False
            elif item is "birth_date":
                if not valid_date(person[item]):
                    valid_file = False
    return valid_file