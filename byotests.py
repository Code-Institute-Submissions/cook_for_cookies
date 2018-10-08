def test_guess_matches_answer(actual, expected):
    assert expected == actual, "Expected {0}, got {1}".format(expected, actual)
    
def test_guess_does_not_match_answer(actual, expected):
    assert expected == actual, "Expected {0}, got {1}".format(expected, actual)
    
def test_guess_is_blank(actual, expected):
    assert expected == actual, "Expected {0}, got {1}".format(expected, actual)