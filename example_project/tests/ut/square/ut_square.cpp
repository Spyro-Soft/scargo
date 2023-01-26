#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"

#include "square.hpp"

TEST_CASE("testing function square (part 1)")
{
    CHECK(square(1) == 1);
    CHECK(square(2) == 4);
}

TEST_CASE("testing function square (part 2)")
{
    CHECK(square(3) == 9);
    CHECK(square(4) == 16);
}
