#!/usr/bin/env python3

""" Module to test papers.py  """

# imports one per line
import os
import json
import re
from exercise2 import decide

__author__ = "Darius Chow and Ryan Prance, Adopted from: Susan Sim"
__email__ = "darius.chow@mail.utoronto.ca, ryan.prance@mail.utoronto.ca, ses@drsusansim.org"
__copyright__ = "Adopted from: 2015 Susan Sim"
__license__ = "MIT License"

__status__ = "Exercise"

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
with open(COUNTRIES_FILE, "r") as countries_file:
    countries_content = countries_file.read()
    COUNTRIES = json.loads(countries_content)

REQUIRED_FIELDS = ("first_name", "last_name", "birth_date", "passport", "home", "from", "entry_reason")
LOCATION_FIELDS = ("home", "from", "via")
REQUIRED_FIELDS_LOCATION = ("city", "region", "country")
REASON_FOR_ENTRY = ('returning', 'visiting')
'''
DATE_TODAY is a string of the format YYYY-MM-DD representing today's date.
'''
DATE_TODAY = "2015-12-16"


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
                    assert valid_passport(person[item]) is True
        assert required_fields_included is False


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
        for item in LOCATION_FIELDS:
            if item in person:
                if person[item]['country'] not in COUNTRIES:
                    unknown_location_found = True
        assert unknown_location_found


def test_decide_unknown_locations():
    """
    Travellers have locations listed that are unknown. Assuming no missing required fields and no missing fields from
    locations.
    """
    assert decide("test_decide_unknown_locations.json", COUNTRIES_FILE) == ["Reject"] * 5


def test_decide_kan_citizens_file():
    """
    Ensure that the file contains travellers that have are KAN citizens and from/via locations that do not have
    medical advisories.
    """
    with open("test_decide_KAN_citizens.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)

    assert valid_file_contents(citizen_json)
    for person in citizen_json:
        assert person["home"]["country"] == "KAN"
        location_fields_to_check = LOCATION_FIELDS[1:]  # Excludes home location field of country_code KAN
        for item in location_fields_to_check:
            if item in person:
                country_code = person[item]['country']
                assert COUNTRIES[country_code]['medical_advisory'] == ""


def test_decide_kan_citizens():
    """
    Travellers that have their home location as KAN. These travellers did not travel from or through a country with
    a medical advisory and all required information is present.
    """
    assert decide("test_decide_KAN_citizens.json", COUNTRIES_FILE) == ["Accept"] * 3


def test_decide_visitors_require_visas_valid_visas_file():
    """
    Ensure that the file contains travellers that have are visitors, from locations that require visas, and they
    have valid visas. No visitors travelled through or from a country with a medical advisory.
    """
    with open("test_decide_visitors_require_visas_valid_visas.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)

    assert valid_file_contents(citizen_json)
    for person in citizen_json:
        country_code = person["home"]["country"]
        assert country_code != "KAN"
        assert COUNTRIES[country_code]['visitor_visa_required'] == "1"
        valid = False
        assert "visa" in person
        if "visa" in person:
            if valid_visa(person["visa"], DATE_TODAY):
                valid = True
        assert valid
        for item in LOCATION_FIELDS:
            if item in person:
                country_code_check_medical_advisory = person[item]['country']
                assert COUNTRIES[country_code_check_medical_advisory]['medical_advisory'] == ""


def test_decide_visitors_require_visas_valid_visas():
    """
    Visitors that have their home location other than KAN (but still a valid location), and because of their home
    countries, they require a visa to enter. Their visas are valid. These travellers did not travel from or through
    a country with a medical advisory and all required information is present.
    """
    assert decide("test_decide_visitors_require_visas_valid_visas.json", COUNTRIES_FILE) == ["Accept"] * 4


def test_decide_visitors_require_visas_invalid_visas_file():
    """
    Ensure that the file contains travellers that are visitors, from locations that require visas, and they
    do not have valid visas. No visitors travelled through or from a country with a medical advisory.
    """
    with open("test_decide_visitors_require_visas_invalid_visas.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)

    assert valid_file_contents(citizen_json)
    for person in citizen_json:
        country_code = person["home"]["country"]
        assert country_code != "KAN"
        assert COUNTRIES[country_code]['visitor_visa_required'] == "1"
        invalid_visa = True
        if "visa" in person:
            if valid_visa(person["visa"], DATE_TODAY):
                invalid_visa = False
        assert invalid_visa
        for item in LOCATION_FIELDS:
            if item in person:
                country_code_check_medical_advisory = person[item]['country']
                assert COUNTRIES[country_code_check_medical_advisory]['medical_advisory'] == ""


def test_decide_visitors_require_visas_invalid_visas():
    """
    Visitors that have their home location other than KAN (but still a valid location), and because of their home
    countries, they require a visa to enter. Their visas are invalid/expired because they are older than 2 years.
    These travellers did not travel from or through a country with a medical advisory and all required information
    is present.
    """
    assert decide("test_decide_visitors_require_visas_invalid_visas.json", COUNTRIES_FILE) == ["Reject"] * 4


def test_decide_visitors_visas_not_needed_file():
    """
    Ensure that the file contains travellers that are visitors, from locations that do not require visas.
    No visitors travelled through or from a country with a medical advisory.
    """
    with open("test_decide_visitors_visas_not_needed.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)

    assert valid_file_contents(citizen_json)
    for person in citizen_json:
        country_code = person["home"]["country"]
        assert country_code != "KAN"
        assert COUNTRIES[country_code]['visitor_visa_required'] == "0"
        for item in LOCATION_FIELDS:
            if item in person:
                country_code_check_medical_advisory = person[item]['country']
                assert COUNTRIES[country_code_check_medical_advisory]['medical_advisory'] == ""


def test_decide_visitors_visas_not_needed():
    """
    Visitors that have their home location other than KAN (but still a valid location), but because of their home
    countries, they do not require a visa to enter. These travellers did not travel from or through a country with
    a medical advisory and all required information is present.
    """
    assert decide("test_decide_visitors_visas_not_needed.json", COUNTRIES_FILE) == ["Accept"] * 1


def test_decide_kan_citizens_via_country_with_medical_advisory_file():
    """
    Ensure that the file contains travellers that KAN citizens. Citizens travelled through or from a country
    with a medical advisory.
    """
    with open("test_decide_KAN_citizens_via_country_with_medical_advisory.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)

    assert valid_file_contents(citizen_json)
    for person in citizen_json:
        traveled_via_medical_advisory_country = False
        for item in person:
            if item == "home":
                assert person["home"]["country"] == "KAN"
            location_fields_to_check = LOCATION_FIELDS[1:]  # Excludes home location field of country_code KAN
            if item in location_fields_to_check:
                country_code = person[item]['country']
                if COUNTRIES[country_code]['medical_advisory'] != "":
                    traveled_via_medical_advisory_country = True
        assert traveled_via_medical_advisory_country


def test_decide_kan_citizens_via_country_with_medical_advisory():
    """
    Testing for KAN citizens that travelled from or via a country with a medical advisory. All required information
    is present.
    """
    assert decide("test_decide_KAN_citizens_via_country_with_medical_advisory.json", COUNTRIES_FILE) ==\
        ["Quarantine"] * 4


def test_decide_visitors_via_country_with_medical_advisory_file():
    """
    Ensure that the file contains travellers that are visitors. Visitors travelled through or from a country with a
    medical advisory. All visitors have or do not need valid visa.
    """
    with open("test_decide_visitors_via_country_with_medical_advisory.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)

    assert valid_file_contents(citizen_json)
    for person in citizen_json:
        country_code = person["home"]["country"]
        assert country_code != "KAN"
        if COUNTRIES[country_code]['visitor_visa_required'] == "1":
            visa_valid = False
            assert "visa" in person
            if "visa" in person:
                if valid_visa(person["visa"], DATE_TODAY):
                    visa_valid = True
            assert visa_valid
        traveled_via_medical_advisory_country = False
        location_fields_to_check = LOCATION_FIELDS[1:]  # Excludes home location field
        for item in location_fields_to_check:
            if item in person:
                country_code = person[item]['country']
                if COUNTRIES[country_code]['medical_advisory'] != "":
                    traveled_via_medical_advisory_country = True
        assert traveled_via_medical_advisory_country


def test_decide_visitors_via_country_with_medical_advisory():
    """
    Testing for visitors that are approved thus far (no required information missing, everything is valid, visa is
    present if required), but travelled from or via a country with a medical advisory.
    """
    assert decide("test_decide_visitors_via_country_with_medical_advisory.json", COUNTRIES_FILE) ==\
        ["Quarantine"] * 4


def test_decide_visitors_invalid_visa_via_country_with_medical_advisory_file():
    """
    Ensure that the file contains travellers that are visitors. Visitors travelled through or from a country with a
    medical advisory. All visitors are from a country that requires a visitor_visa, but these travellers do not have
    valid visas.
    """
    with open("test_decide_visitors_invalid_visa_via_country_with_medical_advisory.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)

    assert valid_file_contents(citizen_json)
    for person in citizen_json:
        country_code = person["home"]["country"]
        assert country_code != "KAN"
        assert COUNTRIES[country_code]['visitor_visa_required'] == "1"
        invalid_visa = True
        if "visa" in person:
            if valid_visa(person["visa"], DATE_TODAY):
                invalid_visa = False
        assert invalid_visa
        traveled_via_medical_advisory_country = False
        location_fields_to_check = LOCATION_FIELDS[1:]  # Excludes home location field
        for item in location_fields_to_check:
            if item in person:
                country_code = person[item]['country']
                if COUNTRIES[country_code]['medical_advisory'] != "":
                    traveled_via_medical_advisory_country = True
        assert traveled_via_medical_advisory_country


def test_decide_visitors_invalid_visa_via_country_with_medical_advisory():
    """
    Testing for visitors that do not have a valid visa and has travelled through or from a country with a medical
    advisory.
    """
    assert decide("test_decide_visitors_invalid_visa_via_country_with_medical_advisory.json", COUNTRIES_FILE) ==\
        ["Reject"] * 4

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
    d1 = {'city': 'city_name', 'region': 'region_name', 'country': 'country_name'}
    assert valid_location_field(d1)
    d2 = {'city': 'city_name', 'country': 'country_name', 'region': 'region_name'}
    assert valid_location_field(d2)
    d3 = {'city': 'city_name', 'province': 'province_name', 'country': 'country_name'}
    assert valid_location_field(d3) is False
    d4 = {'municipality': 'municipality_name', 'state': 'state_name', 'country': 'country_name'}
    assert valid_location_field(d4) is False
    d5 = {'city': 'city_name', 'country': 'country_name'}
    assert valid_location_field(d5) is False
    d6 = {'city': 'city_name', 'region': 'region_name', 'province': 'province_name', 'country': 'country_name'}
    assert valid_location_field(d6) is False


def valid_visa(visa, date_today):
    """
    This function checks to see if a visa is valid, as defined by having a visa number of five groups of
    alphanumeric characters (case-insensitive), separated by dashes, and a date within the past two years.

    :param visa: a dictionary with "code" and "date" that represents a visa number and date respectively
    :param date_today: string that represents a passport or visa number
    :return: True, if the string conforms to the regular expression, False otherwise.
    """

    valid_regex = re.compile(r'^([\dA-Za-z]{5}-){4}[\dA-Za-z]{5}$')
    valid_regex_match = valid_regex.search(visa["code"])
    valid_code = True
    if valid_regex_match is None:
        valid_code = False
    return valid_code and date_within_two_years(visa["date"], date_today)


def test_valid_visa():
    d1 = {"date": "2015-02-24", "code": "6P294-42HR2-95PSF-93NFF-2TEWF"}
    assert valid_visa(d1, "2015-12-16") is True
    d2 = {"date": "2013-12-25", "code": "TJq2R-25stx-Fyc52-02rm0-420DS"}
    assert valid_visa(d2, "2015-12-16") is True
    d3 = {"date": "2015-02-24", "code": "33T0R-8T3T2-W_C77-243GE-42O_D"}
    assert valid_visa(d3, "2015-12-16") is False
    d4 = {"date": "2015-02-24", "code": "T2EW5-WT255-019RW-2RWS4-42FFX-TNX2R"}
    assert valid_visa(d4, "2015-12-16") is False
    d5 = {"date": "2013-12-17", "code": "TJq2R-25stx-Fyc52-02rm0-420DS"}
    assert valid_visa(d5, "2015-12-16")
    d6 = {"date": "2013-12-01", "code": "TJq2R-25stx-Fyc52-02rm0-420DS"}
    assert valid_visa(d6, "2015-12-16") is False


def date_within_two_years(date_to_test, date_today):
    """
    Determine if the date_to_test is within two years of the date_today. Assumption: date_to_test is less-than/before
    date_today. Assumption: the date is a valid date.
    :param date_to_test: a string in the form of "YYYY-MM-DD" representing a date
    :param date_today: a string in the form of "YYYY-MM-DD" representing a date
    :return: True if the date_to_test is within or greater than 2 years. False otherwise
    """
    year_test = int(date_to_test[:4])
    month_test = int(date_to_test[5:7])
    day_test = int(date_to_test[8:])

    year_today = int(date_today[:4])
    month_today = int(date_today[5:7])
    day_today = int(date_today[8:])

    if year_test < (year_today - 2):
        within_two_years = False
    elif year_test > (year_today - 2):
        within_two_years = True
    elif month_test < month_today:
        within_two_years = False
    elif month_test > month_today:
        within_two_years = True
    elif day_test < day_today:
        within_two_years = False
    else:
        within_two_years = True
    return within_two_years


def test_date_within_two_years():
    assert date_within_two_years("2014-03-04", "2015-12-16") is True
    assert date_within_two_years("2013-03-04", "2015-12-16") is False
    assert date_within_two_years("2012-03-04", "2015-12-16") is False
    assert date_within_two_years("2011-03-04", "2015-12-16") is False
    assert date_within_two_years("2013-11-17", "2015-11-16") is True
    assert date_within_two_years("2013-11-16", "2015-11-16") is True
    assert date_within_two_years("2013-11-15", "2015-11-16") is False
    assert date_within_two_years("2013-10-17", "2015-11-16") is False


def valid_passport(passport_number):
    """
    This function checks to see if a passport number is valid, as defined by having five groups of
    alphanumeric characters (case-insensitive), separated by dashes.

    :param passport_number: string that represents a passport or visa number
    :return: True, if the string conforms to the regular expression, False otherwise.
    """
    valid_regex = re.compile(r'^([\dA-Za-z]{5}-){4}[\dA-Za-z]{5}$')
    valid_regex_match = valid_regex.search(passport_number)
    valid = True
    if valid_regex_match is None:
        valid = False
    return valid


def test_valid_passport():
    s1 = "6P294-42HR2-95PSF-93NFF-2TEWF"
    assert valid_passport(s1) is True
    s2 = "TJq2R-25stx-Fyc52-02rm0-420DS"
    assert valid_passport(s2) is True
    s3 = "33T0R-8T3T2-W_C77-243GE-42O_D"
    assert valid_passport(s3) is False
    s4 = "T2EW5-WT255-019RW-2RWS4-42FFX-TNX2R"
    assert valid_passport(s4) is False


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
        month = int(date[5:7])
        day = int(date[8:])
        if 12 < month or month < 1 or 31 < day or day < 1:
            valid = False
    return valid


def test_valid_date():
    assert valid_date("1952-12-25") is True
    assert valid_date("2002-01-05") is True
    assert valid_date("195-12-25") is False
    assert valid_date("1952-13-05") is False
    assert valid_date("1982-02-32") is False
    assert valid_date("1972-3-9") is False


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
                if not valid_passport(person[item]):
                    valid_file = False
            elif item is "visa":
                if not valid_visa(person[item]['code'], DATE_TODAY) or not valid_date(person[item]['date']):
                    valid_file = False
            elif item is "entry_reason":
                if person[item] not in REASON_FOR_ENTRY:
                    valid_file = False
            elif item is "birth_date":
                if not valid_date(person[item]):
                    valid_file = False
    return valid_file