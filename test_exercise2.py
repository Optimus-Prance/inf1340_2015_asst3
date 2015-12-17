#!/usr/bin/env python3

""" Module to test papers.py  """

# imports one per line
import os
import json
import re
from exercise2 import decide, valid_passport_format, valid_date_format, has_valid_visa,\
    valid_visa_format, travelled_via_country_with_medical_advisory

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

    assert valid_file_contents(citizen_json) is False

    for person in citizen_json:
        required_fields_included = True
        for item in REQUIRED_FIELDS:
            if item not in person:
                required_fields_included = False
                break
            else:
                if item in LOCATION_FIELDS:
                    if not valid_location_field(person[item]):
                        required_fields_included = False
                elif item is "passport" and "passport" in person:
                    assert valid_passport_format(person[item]) is True
        assert required_fields_included is False


def test_decide_missing_required_information():
    """
    Travellers have required information that is missing, including incomplete location information.
    """
    assert decide("test_decide_missing_required_information.json", COUNTRIES_FILE) == ["Reject"] * 16


def test_decide_unknown_locations_file():
    """
    Ensure that the file contains travellers that have locations listed that are unknown, and that they have no
    missing information that is required.
    """
    with open("test_decide_unknown_locations.json", "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)

    for person in citizen_json:
        for item in REQUIRED_FIELDS:
            assert item in person
        required_location_fields = LOCATION_FIELDS[:2]
        optional_location_fields = LOCATION_FIELDS[2:]
        for item in required_location_fields:
            assert item in person
            for field in REQUIRED_FIELDS_LOCATION:
                assert field in person[item]
        for item in optional_location_fields:
            if item in person:
                for field in REQUIRED_FIELDS_LOCATION:
                    assert field in person[item]
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
        if has_valid_visa(person):
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
        if has_valid_visa(person):
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
            if has_valid_visa(person):
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
        if has_valid_visa(person):
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
    Finds out if a location field (in the form of a dictionary) is a validly filled out and the country_code matches
    a country in countries.json. Returns a boolean.

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
        if valid:
            country_code = location["country"]
            if country_code not in COUNTRIES and country_code != "KAN":
                valid = False
    return valid


def test_valid_location_field():
    d1 = {'city': 'city_name', 'region': 'region_name', 'country': 'LUG'}
    assert valid_location_field(d1)
    d2 = {'city': 'city_name', 'country': 'III', 'region': 'region_name'}
    assert valid_location_field(d2)
    d3 = {'city': 'city_name', 'country': 'AAA', 'region': 'region_name'}
    assert valid_location_field(d3) is False
    d4 = {'city': 'city_name', 'province': 'province_name', 'country': 'III'}
    assert valid_location_field(d4) is False
    d5 = {'municipality': 'municipality_name', 'state': 'state_name', 'country': 'III'}
    assert valid_location_field(d5) is False
    d6 = {'city': 'city_name', 'country': 'III'}
    assert valid_location_field(d6) is False
    d7 = {'city': 'city_name', 'region': 'region_name', 'province': 'province_name', 'country': 'III'}
    assert valid_location_field(d7) is False


def test_valid_visa_format():
    """
    Tests the valid_visa_format function. A valid visa format should be two groups of five alphanumeric characters
    separated by a dash.
    """
    assert valid_visa_format("52NDX-2RSEF") is True
    assert valid_visa_format("2nrx3-fkWW3") is True
    assert valid_visa_format("2nrx3-fkWW32") is False
    assert valid_visa_format("2nr_3-fkWW2") is False
    assert valid_visa_format("2nrx3-fkWW2-WJD23") is False
    assert valid_visa_format("2nrx3-fkWW") is False
    assert valid_visa_format("2rjxefn2rx") is False


def test_has_valid_visa():
    p1 = {"passport": "6P294-42HR2-95PSF-93NFF-2T5WF",
          "first_name": "JACK",
          "last_name": "DOE",
          "birth_date": "1938-12-21",
          "home": {"city": "Bala",
                   "region": "ON",
                   "country": "KAN"},
          "visa": {"code": "BER4r-WDN39",
                   "date": "2015-02-24"},
          "entry_reason": "returning",
          "from": {"city": "Wumpus",
                   "region": "Headdeskia",
                   "country": "JIK"}}
    assert has_valid_visa(p1) is True
    p2 = {"passport": "6P294-42HR2-95PSF-93NFF-2T5WF",
          "first_name": "JACK",
          "last_name": "DOE",
          "birth_date": "1938-12-21",
          "home": {"city": "Bala",
                   "region": "ON",
                   "country": "KAN"},
          "entry_reason": "returning",
          "from": {"city": "Wumpus",
                   "region": "Headdeskia",
                   "country": "JIK"}}
    assert has_valid_visa(p2) is False
    p3 = {"passport": "6P294-42HR2-95PSF-93NFF-2T5WF",
          "first_name": "JACK",
          "last_name": "DOE",
          "birth_date": "1938-12-21",
          "home": {"city": "Bala",
                   "region": "ON",
                   "country": "KAN"},
          "visa": {"code": "BER4rWDN39",
                   "date": "2015-02-24"},
          "entry_reason": "returning",
          "from": {"city": "Wumpus",
                   "region": "Headdeskia",
                   "country": "JIK"}}
    assert has_valid_visa(p3) is False
    p4 = {"passport": "6P294-42HR2-95PSF-93NFF-2T5WF",
          "first_name": "JACK",
          "last_name": "DOE",
          "birth_date": "1938-12-21",
          "home": {"city": "Bala",
                   "region": "ON",
                   "country": "KAN"},
          "visa": {"code": "BER4r-WDN39",
                   "date": "2010-02-24"},
          "entry_reason": "returning",
          "from": {"city": "Wumpus",
                   "region": "Headdeskia",
                   "country": "JIK"}}
    assert has_valid_visa(p4) is False


def test_valid_passport():
    s1 = "6P294-42HR2-95PSF-93NFF-2TEWF"
    assert valid_passport_format(s1) is True
    s2 = "TJq2R-25stx-Fyc52-02rm0-420DS"
    assert valid_passport_format(s2) is True
    s3 = "33T0R-8T3T2-W_C77-243GE-42O_D"
    assert valid_passport_format(s3) is False
    s4 = "T2EW5-WT255-019RW-2RWS4-42FFX-TNX2R"
    assert valid_passport_format(s4) is False


def test_valid_date_format():
    assert valid_date_format("1952-12-25") is True
    assert valid_date_format("2002-01-05") is True
    assert valid_date_format("2002-01-31") is True
    assert valid_date_format("2000-02-28") is True
    assert valid_date_format("2002-02-30") is False
    assert valid_date_format("2002-04-31") is False
    assert valid_date_format("195-12-25") is False
    assert valid_date_format("1952-13-05") is False
    assert valid_date_format("1982-02-32") is False
    assert valid_date_format("1972-3-9") is False
    assert valid_date_format("03-09-2000") is False


def test_travelled_via_country_with_medical_advisory():
    countries = {"JIK": {"code": "JIK",
                         "name": "Jikland",
                         "visitor_visa_required": "0",
                         "transit_visa_required": "0",
                         "medical_advisory": ""},
                 "KRA": {"code": "KRA",
                         "name": "Kraznoviklandstan",
                         "visitor_visa_required": "0",
                         "transit_visa_required": "0",
                         "medical_advisory": ""},
                 "LUG": {"code": "LUG",
                         "name": "Democratic Republic of Lungary",
                         "visitor_visa_required": "1",
                         "transit_visa_required": "1",
                         "medical_advisory": "MUMPS"}}
    t1 = {"passport": "6P294-42HR2-95PSF-93NFF-2T5WF",
          "first_name": "JACK",
          "last_name": "DOE",
          "birth_date": "1938-12-21",
          "home": {"city": "Bala",
                   "region": "ON",
                   "country": "KAN"},
          "entry_reason": "returning",
          "from": {"city": "Wumpus",
                   "region": "Headdeskia",
                   "country": "JIK"}}
    assert travelled_via_country_with_medical_advisory(t1,countries) is False
    t2 = {"passport": "6P294-42HR2-95PSF-93NFF-2T5WF",
          "first_name": "JACK",
          "last_name": "DOE",
          "birth_date": "1938-12-21",
          "home": {"city": "Bala",
                   "region": "ON",
                   "country": "KAN"},
          "entry_reason": "returning",
          "visa": {"code": "BER4r-WDN39",
                   "date": "2014-03-29"},
          "from": {"city": "Wumpus",
                   "region": "Headdeskia",
                   "country": "JIK"}}
    assert travelled_via_country_with_medical_advisory(t2,countries) is False
    t3 = {"passport": "6P294-42HR2-95PSF-93NFF-2T5WF",
          "first_name": "JACK",
          "last_name": "DOE",
          "birth_date": "1938-12-21",
          "home": {"city": "Bala",
                   "region": "ON",
                   "country": "LUG"},
          "entry_reason": "returning",
          "from": {"city": "Wumpus",
                   "region": "Headdeskia",
                   "country": "JIK"},
          "via": {"city": "Lasher",
                   "region": "Phuy",
                   "country": "KRA"}}
    assert travelled_via_country_with_medical_advisory(t3,countries) is False
    t4 = {"passport": "6P294-42HR2-95PSF-93NFF-2T5WF",
          "first_name": "JACK",
          "last_name": "DOE",
          "birth_date": "1938-12-21",
          "home": {"city": "Bala",
                   "region": "ON",
                   "country": "JIK"},
          "entry_reason": "returning",
          "from": {"city": "Wumpus",
                   "region": "Headdeskia",
                   "country": "LUG"}}
    assert travelled_via_country_with_medical_advisory(t4,countries) is True
    t5 = {"passport": "6P294-42HR2-95PSF-93NFF-2T5WF",
          "first_name": "JACK",
          "last_name": "DOE",
          "birth_date": "1938-12-21",
          "home": {"city": "Bala",
                   "region": "ON",
                   "country": "KAN"},
          "entry_reason": "returning",
          "from": {"city": "Wumpus",
                   "region": "Headdeskia",
                   "country": "KRA"},
          "via": {"city": "Lasher",
                   "region": "Phuy",
                   "country": "LUG"}}
    assert travelled_via_country_with_medical_advisory(t5,countries) is True
    t6 = {"passport": "6P294-42HR2-95PSF-93NFF-2T5WF",
          "first_name": "JACK",
          "last_name": "DOE",
          "birth_date": "1938-12-21",
          "home": {"city": "Bala",
                   "region": "ON",
                   "country": "KAN"},
          "entry_reason": "returning",
          "from": {"city": "Wumpus",
                   "region": "Headdeskia",
                   "country": "LUG"},
          "via": {"city": "Lasher",
                   "region": "Phuy",
                   "country": "LUG"}}
    assert travelled_via_country_with_medical_advisory(t6,countries) is True



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
                if not valid_passport_format(person[item]):
                    valid_file = False
            elif item is "visa":
                if not valid_visa(person[item]['code'], DATE_TODAY) or not valid_date_format(person[item]['date']):
                    valid_file = False
            elif item is "entry_reason":
                if person[item] not in REASON_FOR_ENTRY:
                    valid_file = False
            elif item is "birth_date":
                if not valid_date_format(person[item]):
                    valid_file = False
    return valid_file