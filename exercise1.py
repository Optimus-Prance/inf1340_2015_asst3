#!/usr/bin/env python3

""" Assignment 3, Exercise 2, INF1340, Fall, 2015. DBMS

This module performs table operations on database tables
implemented as lists of lists. """

__author__ = "Darius Chow and Ryan Prance, Adopted from: Susan Sim"
__email__ = "darius.chow@mail.utoronto.ca, ryan.prance@mail.utoronto.ca, ses@drsusansim.org"
__copyright__ = "Adopted from: 2015 Susan Sim"
__license__ = "MIT License"


#####################
# HELPER FUNCTIONS ##
#####################
EMPLOYEES = [["Surname", "FirstName", "Age", "Salary"],
             ["Smith", "Mary", 25, 2000],
             ["Black", "Lucy", 40, 3000],
             ["Verdi", "Nico", 36, 4500],
             ["Smith", "Mark", 40, 3900]]
R1 = [["Employee", "Department"],
      ["Smith", "sales"],
      ["Black", "production"],
      ["White", "production"]]


def remove_duplicates(l):
    """
    Removes duplicates from l, where l is a List of Lists.
    :param l: a List
    """

    d = {}
    result = []
    for row in l:
        if tuple(row) not in d:
            result.append(row)
            d[tuple(row)] = True

    return result


def deep_copy(t):
    dup_list = []
    for row in t:
        copy_cell = []
        for i in row:
            copy_cell.append(i)

        dup_list.append(copy_cell)

    return dup_list


class UnknownAttributeException(Exception):
    """
    Raised when attempting set operations on a table
    that does not contain the named attribute
    """
    pass


def selection(t, f):
    """
    Perform select operation on table t that satisfy condition f.

    Example:
    > R = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
    ># Define function f that returns True iff
    > # the last element in the row is greater than 3.
    > def f(row): row[-1] > 3
    > select(R, f)
    [["A", "B", "C"], [4, 5, 6]]

    We assume that the function is always compatible with the table.
    (e.g. if the table has 3 columns, the function will not try to access the 4th column)
    
    :param t: A table in the form of a list of lists with the first item being a list of strings denoting the
      attribute names
    :param f: A function that takes in a row of a table (denoted by a list) and returns a boolean.
    :return: A table with only those rows for which when applied the function f, returns True. Otherwise, if the
      resulting table is empty, None is returned.
    """
    new = []
    if len(t) < 2:
        return None
    for row in t:
        if f(row) is True:
            new.append(row)
    if len(new) <= 1:
        return None
    return new


def projection(t, r):
    """
    Perform projection operation on table t
    using the attributes subset r.

    Example:
    > R = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
    > projection(R, ["A", "C"])
    [["A", "C"], [1, 3], [4, 6]]

    :param t: A table in the form of a list of lists with the first item being a list of strings denoting the
      attribute names.
    :param r: A list of attributes denoted by a list of strings.
    :return: A table in the form of a list of lists with the first item being a list of strings denoting the list of
      attributes. Otherwise, if the table is empty, None is returned.
    """
    if r == [] or t == [] or len(t) < 2:
        return None

    plist = []
    # Fill out plist, which lists the indices of the matched attributes
    for attr in r:
        if attr in t[0]:
            pos = t[0].index(attr)
            if pos not in plist:
                plist.append(pos)
        else:
            raise UnknownAttributeException

    new = []
    for row in t:
        container = []
        for attr_index in plist:
            container.append(row[attr_index])
        new.append(container)
    if len(new) == 0:
        return None
    else:
        return new


def cross_product(t1, t2):
    """
    Return the cross-product of tables t1 and t2.

    Example:
    > R1 = [["A", "B"], [1,2], [3,4]]
    > R2 = [["C", "D"], [5,6]]
    [["A", "B", "C", "D"], [1, 2, 5, 6], [3, 4, 5, 6]]

    :param t1: A table as denoted by a list of lists with the first list item representing the attributes in the form
      of a list of strings.
    :param t2: A table as denoted by a list of lists with the first list item representing the attributes in the form
      of a list of strings.
    :return: A table (list of lists) with the first list depicting the attributes of the table. Otherwise, if no rows
      are in the table, None is returned
    """

    copy_table1 = deep_copy(t1)
    copy_table2 = deep_copy(t2)

    new = []

    # create new schema
    for category in copy_table2[0]:
        copy_table1[0].append(category)
    new.append(copy_table1[0])
    # make table content
    if copy_table1 != copy_table2:
        for row in copy_table1[1:]:

            for i in copy_table2[1:]:
                new.append(row + i)

    if len(new) < 2:
        return None

    return new
