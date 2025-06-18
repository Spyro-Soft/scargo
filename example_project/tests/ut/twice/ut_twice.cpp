#include <gtest/gtest.h>
#include <twice.hpp>

TEST(TwiceTestCase, BasicAssertion)
{
    EXPECT_TRUE(twice(1) == 2);
    EXPECT_TRUE(twice(2) == 4);
    EXPECT_TRUE(twice(3) == 6);
    EXPECT_TRUE(twice(4) == 8);
}