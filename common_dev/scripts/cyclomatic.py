#!/usr/bin/env python3

import lizard  # type: ignore[import-untyped]

# to exclude directory use -x <dir_path> param
params = ["lizard", "/scargo/", "-C", "25", "-w"]

if __name__ == "__main__":
    lizard.main(params)
