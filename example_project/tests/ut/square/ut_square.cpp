#include <gtest/gtest.h>
#include <square.hpp>

TEST(SquareTestCase, BasicAssertion1)
{
    EXPECT_TRUE(square(1) == 1);
    EXPECT_TRUE(square(2) == 4);
}

TEST(SquareTestCase, BasicAssertion2)
{
    EXPECT_TRUE(square(3) == 9);
    EXPECT_TRUE(square(4) == 16);
}