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

R2 = [["Department", "Head"],
      ["production", "Mori"],
      ["sales", "Brown"]]

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
    """
    new =[]
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

    """
    if r == [] or  t == [] or len(t) < 2:
        return None

    plist = []
    #Fill out plist, which lists the indices of the matched attributes
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




def cross_product(t1,t2):
    """
    Return the cross-product of tables t1 and t2.

    Example:
    > R1 = [["A", "B"], [1,2], [3,4]]
    > R2 = [["C", "D"], [5,6]]
    [["A", "B", "C", "D"], [1, 2, 5, 6], [3, 4, 5, 6]]


    """
    new = []


    #create new schema
    for category in t2[0]:
        t1[0].append(category)
    new.append(t1[0])
    #make table content
    if t1 != t2:
        for row in t1[1:]:
            step = 0
            for i in t2[1:]:
                new.append(row + i)

    if len(new) < 2:
        return None

    return new


#havent got this to work if t1 and t2 are the same