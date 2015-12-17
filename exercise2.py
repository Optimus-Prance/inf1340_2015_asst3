#!/usr/bin/env python3

""" Assignment 3, Exercise 2, INF1340, Fall, 2015. Kanadia

Computer-based immigration office for Kanadia

"""

import re
import json
import datetime

__author__ = "Darius Chow and Ryan Prance, Adopted from: Susan Sim"
__email__ = "darius.chow@mail.utoronto.ca, ryan.prance@mail.utoronto.ca, ses@drsusansim.org"
__copyright__ = "Adopted from: 2015 Susan Sim"
__license__ = "MIT License"


######################
## global constants ##
######################
REQUIRED_FIELDS = ["passport", "first_name", "last_name",
                   "birth_date", "home", "entry_reason", "from"]
LOCATION_FIELDS = ("home", "from", "via")
REQUIRED_FIELDS_LOCATION = ("city", "region", "country")

######################
## global variables ##
######################
'''
countries:
dictionary mapping country codes (lowercase strings) to dictionaries
containing the following keys:
"code","name","visitor_visa_required",
"transit_visa_required","medical_advisory"
'''
COUNTRIES = None


#####################
# HELPER FUNCTIONS ##
#####################
def is_more_than_x_years_ago(x, date_string):
    """
    Check if date is less than x years ago.

    :param x: int representing years
    :param date_string: a date string in format "YYYY-mm-dd"
    :return: True if date is less than x years ago; False otherwise.
    """

    now = datetime.datetime.now()
    x_years_ago = now.replace(year=now.year - x)
    date = datetime.datetime.strptime(date_string, '%Y-%m-%d')

    return (date - x_years_ago).total_seconds() < 0


def decide(input_file, countries_file):
    """
    Decides whether a traveller's entry into Kanadia should be accepted according to business rules. If a traveller has
    any of the required information fields (first_name, last_name, birth_date, passport, home, from, and entry_reason)
    missing, or if any location is unknown (i.e. not in the list of countries), then entry is denied. A Kanadia
    citizen (as denoted by a entry_reason of 'returning', and the home country as "KAN") will be approved unless
    they travelled from or through a country with a medical advisory, in which case they will be quarantined.
    Non-Kanadia citizens (visitors) will be approved if their home country does not have a visa requirement, or if
    their country does have a visa requirement, they have a valid visa, only if they did not travel through or from
    a country with a medical advisory. If these visitors travelled through or from a country with a medical advisory,
    then they are to be quarantined. Otherwise, if they are required to produce a visa but do not have a valid visa,
    then they will be rejected.

    :param input_file: The name of a JSON formatted file that contains
        cases to decide
    :param countries_file: The name of a JSON formatted file that contains
        country data, such as whether an entry or transit visa is required,
        and whether there is currently a medical advisory
    :return: List of strings. Possible values of strings are:
        "Accept", "Reject", and "Quarantine"
    """
    with open(input_file, "r") as citizen_file:
        citizen_content = citizen_file.read()
    citizen_json = json.loads(citizen_content)
    with open(countries_file, "r") as countries_file:
        countries_content = countries_file.read()
    COUNTRIES = json.loads(countries_content)

    decisions = []

    for person in citizen_json:
        reject = False
        quarantine = False
        accept = False
        if not required_fields_exist(person):
            reject = True
        elif unknown_location_exists(person, COUNTRIES):
            reject = True
        else:
            if person["home"]["country"] == "KAN":  # if visitor's home is Kanadia (KAN)
                accept = True
            elif not visitor_from_country_requiring_visa(person, COUNTRIES):
                accept = True
            elif visitor_from_country_requiring_visa(person, COUNTRIES) and has_valid_visa(person):
                accept = True
            else:
                reject = True

            if travelled_via_country_with_medical_advisory(person, COUNTRIES):
                quarantine = True

        if reject:
            decisions.append("Reject")
        elif quarantine:
            decisions.append("Quarantine")
        elif accept:
            decisions.append("Accept")
        else:
            raise

    return decisions


def valid_passport_format(passport_number):
    """
    This function checks to see if a passport number is valid, as defined by having five groups of
    alphanumeric characters (case-insensitive), separated by dashes.

    :param passport_number: string that represents a passport or visa number
    :return: True, if the string conforms to the valid regular expression, False otherwise.
    """
    valid_regex = re.compile(r'^([\dA-Za-z]{5}-){4}[\dA-Za-z]{5}$')
    valid_regex_match = valid_regex.search(passport_number)
    valid = True
    if valid_regex_match is None:
        valid = False
    return valid


def travelled_via_country_with_medical_advisory(person, countries):
    """
    Checks to see if the traveller came from or through a country with a medical advisory
    :param person: a person's application in the form of a dictionary. It is assumed that there is no missing
    of required information and that the locations they travelled from or through are valid locations (in countries)
    :param countries: a dictionary of country_codes with information like if a country has a medical advisory or not.
    :return: Returns True if the person travelled from or through a country with a medical advisory, False otherwise.
    """
    travelled_through_country_with_medical_advisory = False
    location_fields_to_check = LOCATION_FIELDS[1:]     # Skips checking 'home'
    for item in location_fields_to_check:
        if item in person:
            country_code = person[item]['country']
            if countries[country_code]['medical_advisory'] != "":
                travelled_through_country_with_medical_advisory = True
    return travelled_through_country_with_medical_advisory


def valid_visa_format(visa_code):
    """
    Checks whether a visa code is two groups of five alphanumeric characters
    :param visa_code: alphanumeric string
    :return: Boolean; True if the format is valid, False otherwise

    """
    valid_regex = re.compile(r'^[\dA-Za-z]{5}-[\dA-Za-z]{5}$')
    valid_regex_match = valid_regex.search(visa_code)
    valid = True
    if valid_regex_match is None:
        valid = False
    return valid


def valid_date_format(date_string):
    """
    Checks whether a date has the format YYYY-mm-dd in numbers
    :param date_string: date to be checked
    :return: Boolean True if the format is valid, False otherwise
    """
    valid_regex = re.compile(r'^\d{4}(-\d{2}){2}$')
    valid_regex_match = valid_regex.search(date_string)
    valid = True
    if valid_regex_match is None:
        valid = False
    else:
        year = int(date_string[:4])
        month = int(date_string[5:7])
        day = int(date_string[8:])
        if year < 1900 or year > 2016 or month < 1 or month > 12 or day < 1 or day > 31:
            valid = False
        else:
            if month in [4,6,9,11]:
                if day > 30:
                    valid = False
            elif month == 2:
                if day > 29:
                    valid = False
    return valid


def has_valid_visa(person):
    """
    This function checks to see if the traveller has a visa that is valid, as defined by having a visa number of five
    groups of alphanumeric characters (case-insensitive), separated by dashes, and a date within the past two years.

    :param person: a person's application in the form of a dictionary. It is assumed that there is no missing
    of required information.
    :return: True, if the visa code is valid and the date is not more than 2 years, False otherwise.
    """
    valid_visa = False
    if "visa" in person:
        if "code" in person["visa"] and "date" in person["visa"]:
            valid_visa = valid_visa_format(person["visa"]["code"]) and \
                         not is_more_than_x_years_ago(2, person["visa"]["date"])
    return valid_visa


def visitor_from_country_requiring_visa(person, countries):
    """
    Checks to see if the traveller requires a visa to enter as determined by the home country and the list of countries
    provided by the ministry. We assume that the person's home town is a valid country and is not from Kanadia.
    :param person: a person's application in the form of a dictionary. It is assumed that there is no missing
    of required information and that the locations they travelled from or through are valid locations (in countries)
    :param countries: a dictionary of country_codes with information like if a country has a medical advisory or not.
    :return: Returns True if the person requires a visa to enter Kanadia, False otherwise.
    """
    country_code = person["home"]["country"]
    return countries[country_code]["visitor_visa_required"] == "1"


def unknown_location_exists(person, countries):
    """
    Checks to see if the traveller has any location field be unknown. With the exception of Kanadia (KAN), the
    remaining countries should be listed in the dictionary of countries.
    :param person: a person's application in the form of a dictionary. It is assumed that there is no missing
    required information.
    :param countries: a dictionary of country_codes.
    :return: Returns True if the person has a location that is unknown, False otherwise.
    """
    unknown_location_found = False
    for item in LOCATION_FIELDS:
        if item in person:
            country_code = person[item]["country"]
            if country_code not in countries and country_code != "KAN":
                unknown_location_found = True
                break
    return unknown_location_found

def required_fields_exist(person):
    satisfy = True
    for field in REQUIRED_FIELDS:
        if field not in person:
            satisfy = False
    for field in person:
        if field in LOCATION_FIELDS:
            if not valid_location_field(person[field]):
                satisfy = False
    return satisfy



def valid_location_field(location):
    """
    Finds out if a location field (in the form of a dictionary) is a validly filled out. Returns a boolean.

    :param location: a dictionary
    :return: True the location field is valid. False otherwise.
    """
    valid = True
    if len(location) != 3:
        valid = False
    else:
        for item in REQUIRED_FIELDS_LOCATION:
            if item not in location:
                valid = False
    return valid
