from byotests import *

def areIDsTheSame(Collection1, Collection2):
    if Collection1 == Collection2:
        return True

test_guess_matches_answer(areIDsTheSame(1, 1), True)

print("TEST SUITE MESSAGE - All tests have passed!!!")