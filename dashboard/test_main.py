"""Write tests"""
from main import print_hello


def test_print_hello():
    assert print_hello() == "hello"
