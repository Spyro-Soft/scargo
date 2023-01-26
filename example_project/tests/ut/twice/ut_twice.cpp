#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"

#include "twice.hpp"

TEST_CASE("testing function twice")
{
    CHECK(twice(1) == 2);
    CHECK(twice(2) == 4);
    CHECK(twice(3) == 6);
    CHECK(twice(4) == 8);
}
