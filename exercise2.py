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

    return ["Reject"]


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