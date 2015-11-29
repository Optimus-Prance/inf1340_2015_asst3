#!/usr/bin/env python

""" Assignment 3, Exercise 1, INF1340, Fall, 2015. DBMS

Test module for exercise3.py

"""

__author__ = 'Susan Sim'
__email__ = "ses@drsusansim.org"
__copyright__ = "2015 Susan Sim"
__license__ = "MIT License"

from exercise1 import selection, projection, cross_product


###########
# TABLES ##
###########

EMPLOYEES = [["Surname", "FirstName", "Age", "Salary"],
             ["Smith", "Mary", 25, 2000],
             ["Black", "Lucy", 40, 3000],
             ["Verdi", "Nico", 36, 4500],
             ["Smith", "Mark", 40, 3900]]

R1 = [["Employee", "Department"],
      ["Smith", "sales"],
      ["Black", "production"],
      ["White", "production"]]

R2 = [["Department", "Head"],
      ["production", "Mori"],
      ["sales", "Brown"]]


#####################
# HELPER FUNCTIONS ##
#####################
def is_equal(t1, t2):

    t1.sort()
    t2.sort()

    return t1 == t2


#####################
# FILTER FUNCTIONS ##
#####################
def filter_employees(row):
    """
    Check if employee represented by row
    is AT LEAST 30 years old and makes
    MORE THAN 3500.
    :param row: A List in the format:
        [{Surname}, {FirstName}, {Age}, {Salary}]
    :return: True if the row satisfies the condition.
    """
    return row[-2] >= 30 and row[-1] > 3500


###################
# TEST FUNCTIONS ##
###################

def test_selection():
    """
    Test select operation.
    """
    #Some gets selected, some don't get selected
    result = [["Surname", "FirstName", "Age", "Salary"],
              ["Verdi", "Nico", 36, 4500],
              ["Smith", "Mark", 40, 3900]]

    assert is_equal(result, selection(EMPLOYEES, filter_employees))

    #Selection returns everything
    E_1 = [["Surname", "FirstName", "Age", "Salary"],
           ["Verdi", "Nico", 36, 4500],
           ["Smith", "Mark", 40, 3900]]

    assert is_equal(E_1, selection(E_1, filter_employees))

    #Selection returns nothing
    E_2 = [["Surname", "FirstName", "Age", "Salary"],
           ["Smith", "Mary", 25, 2000],
           ["Black", "Lucy", 40, 3000]]

    assert is_equal(None, selection(E_2, filter_employees))

    #Selection on empty table
    E_3 = [["Surname", "FirstName", "Age", "Salary"]]

    assert is_equal(None, selection(E_3, filter_employees))

def test_projection():
    """
    Test projection operation.
    """
    # Project some attributes
    result = [["Surname", "FirstName"],
              ["Smith", "Mary"],
              ["Black", "Lucy"],
              ["Verdi", "Nico"],
              ["Smith", "Mark"]]

    assert is_equal(result, projection(EMPLOYEES, ["Surname", "FirstName"]))

    # Project all attributes
    attribute_list = ["Surname", "FirstName", "Age", "Salary"]
    empty_table = [attribute_list]
    assert is_equal(result, projection(EMPLOYEES, attribute_list))
    assert is_equal(None,projection(empty_table,attribute_list))

    # Project No attributes
    assert is_equal(None, projection(EMPLOYEES, []))
    assert is_equal(None, projection(empty_table, []))

    # Attribute not found (all mismatch, and partial mismatch)
    try:
        projection(EMPLOYEES, ["LastName", "GivenName"])
        assert False
    except:
        assert True
    try:
        projection(EMPLOYEES, ["Date of Birth", "Income"])
        assert False
    except:
        assert True

def test_cross_product():
    """
    Test cross product operation.
    """

    result_1 = [["Employee", "Department", "Department", "Head"],
                ["Smith", "sales", "production", "Mori"],
                ["Smith", "sales", "sales", "Brown"],
                ["Black", "production", "production", "Mori"],
                ["Black", "production", "sales", "Brown"],
                ["White", "production", "production", "Mori"],
                ["White", "production", "sales", "Brown"]]

    assert is_equal(result_1, cross_product(R1, R2))

    result_2 = [["Department", "Head", "Employee", "Department"],
                ["production", "Mori", "Smith", "sales"],
                ["sales", "Brown", "Smith", "sales"],
                ["production", "Mori", "Black", "production"],
                ["sales", "Brown", "Black", "production"],
                ["production", "Mori", "White", "production"],
                ["sales", "Brown", "White", "production"]]

    assert is_equal(result_2, cross_product(R2, R1))

    # Cross product using larger tables
    result_3 = [["Surname", "FirstName", "Age", "Salary", "Employee", "Department"],
                ["Smith", "Mary", 25, 2000, "Smith", "sales"],
                ["Smith", "Mary", 25, 2000, "Black", "production"],
                ["Smith", "Mary", 25, 2000, "White", "production"],
                ["Black", "Lucy", 40, 3000, "Smith", "sales"],
                ["Black", "Lucy", 40, 3000, "Black", "production"],
                ["Black", "Lucy", 40, 3000, "White", "production"],
                ["Verdi", "Nico", 36, 4500, "Smith", "sales"],
                ["Verdi", "Nico", 36, 4500, "Black", "production"],
                ["Verdi", "Nico", 36, 4500, "White", "production"],
                ["Smith", "Mark", 40, 3900, "Smith", "sales"],
                ["Smith", "Mark", 40, 3900, "Black", "production"],
                ["Smith", "Mark", 40, 3900, "White", "production"]]

    assert is_equal(result_3, cross_product(EMPLOYEES, R1))

    # Cross product of same tables
    result_4 = [["Employee", "Department", "Employee", "Department"],
                ["Smith", "sales", "Smith", "sales"],
                ["Black", "production", "Black", "production"],
                ["White", "production", "White", "production"]]

    assert is_equal(result_4, cross_product(R1, R1))

    # Cross product using table with one row
    table_with_one_row = [["ID Number", "Date of Birth"],
                          [0001, "01/01/2001"]]

    result_5 = [["ID Number", "Date of Birth", "Surname", "FirstName", "Age", "Salary"],
                [0001, "01/01/2001", "Smith", "Mary", 25, 2000],
                [0001, "01/01/2001", "Black", "Lucy", 40, 3000],
                [0001, "01/01/2001", "Verdi", "Nico", 36, 4500],
                [0001, "01/01/2001", "Smith", "Mark", 40, 3900]]

    assert is_equal(result_5, cross_product(table_with_one_row, EMPLOYEES))

    result_6 = [["Surname", "FirstName", "Age", "Salary", "ID Number", "Date of Birth"],
                ["Smith", "Mary", 25, 2000, 0001, "01/01/2001"],
                ["Black", "Lucy", 40, 3000, 0001, "01/01/2001"],
                ["Verdi", "Nico", 36, 4500, 0001, "01/01/2001"],
                ["Smith", "Mark", 40, 3900, 0001, "01/01/2001"]]

    assert is_equal(result_6, cross_product(EMPLOYEES, table_with_one_row))

    result_7 = [["ID Number", "Date of Birth", "ID Number", "Date of Birth"],
                [0001, "01/01/2001", 0001, "01/01/2001"]]

    assert is_equal(result_7, cross_product(table_with_one_row, table_with_one_row))

    # Cross product using empty table
    empty_table = [["ID Number", "Date of Birth"]]
    assert is_equal(None, cross_product(empty_table, R1))
    assert is_equal(None, cross_product(empty_table, R2))
    assert is_equal(None, cross_product(R1, empty_table))
    assert is_equal(None, cross_product(R2, empty_table))