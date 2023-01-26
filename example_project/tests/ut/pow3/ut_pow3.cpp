#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"

#include "pow3.hpp"

TEST_CASE("testing function pow3")
{
    CHECK(pow3(1) == 1);
    CHECK(pow3(2) == 8);
    CHECK(pow3(3) == 27);
}
