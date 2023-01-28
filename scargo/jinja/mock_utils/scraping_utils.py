# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #


def is_multiline(line):
    line = line.rstrip()
    if line.endswith("="):
        return True
    if line.count("(") != line.count(")"):
        return True
    return False


def missing_data_diff(old_data, new_data):
    """
    Prints missing mocks implementations and return True if there is any.
    """
    missing = False
    print("\033[31m")  # red color
    missing_mocks = list(
        set(new_data["missing_mocks"]) - set(old_data["missing_mocks"])
    )
    if missing_mocks:
        missing = True
        print("\nMissing mock file implementation:")
        for i in missing_mocks:
            print(f"    \u00B7 {i}")

    missing_classes = dict_diff(
        old_data["missing_classes"], new_data["missing_classes"]
    )
    if missing_classes:
        missing = True
        print("\nMissing mock class implementation:")
        for key, value in missing_classes.items():
            print(f"    \u00B7 {key}: {value}")

    missing_methods = dict_diff(
        old_data["missing_methods"], new_data["missing_methods"]
    )
    if missing_methods:
        missing = True
        print("\nMissing mock method implementation:")
        for key, value in missing_methods.items():
            print(f"    \u00B7 {key}: {value}")
    print("\033[0m")  # reset color

    return missing


def dict_diff(dict1, dict2):
    """
    Returns the difference between two dictionaries consisting of the key:list pair.
    """
    diffs = {}
    for key, value in dict2.items():
        if key not in dict1.keys():
            diffs[key] = value
            continue
        value_diff = set(value) - set(dict1[key])
        if value_diff:
            diffs[key] = value_diff
    return diffs
