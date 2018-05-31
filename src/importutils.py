import os, sys

def addpath(__file__, path):
    __file__ = os.path.normpath(os.path.abspath(__file__))
    __path__ = os.path.dirname(__file__)
    __added_path__ = os.path.join(__path__, path)

    if __path__ not in sys.path:
        sys.path.insert(0, __path__)
    if __added_path__ not in sys.path:
        sys.path.insert(0, __added_path__)