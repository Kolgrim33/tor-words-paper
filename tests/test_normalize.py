from torwords.normalize import education_level, relationship


def test_education_level():
    assert education_level("High School Diploma") == "high school"
    assert education_level("Masters in Architecture") == "masters"
    assert education_level("PhD in Physics") == "phd"
    assert education_level("Bachelors in Graphic Design") == "bachelors"
    assert education_level("Master's degree") == "masters"


def test_relationship():
    assert relationship("in relationship") == "in a relationship"
    assert relationship("Married") == "married"
