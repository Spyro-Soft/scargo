#include <gtest/gtest.h>
#include <pow3.hpp>

TEST(Pow3TestCase, BasicAssertion)
{
    EXPECT_TRUE(pow3(1) == 1);
    EXPECT_TRUE(pow3(2) == 8);
    EXPECT_TRUE(pow3(3) == 27);
}