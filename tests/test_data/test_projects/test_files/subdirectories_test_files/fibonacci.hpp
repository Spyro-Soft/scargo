//
// Copyright
//

#pragma once

#ifndef FILE_FIBONACCI_HPP
#define FILE_FIBONACCI_HPP

inline long long int Fibonacci(long long int n)
{
    return (n == 0 || n == 1) ? 1 : Fibonacci(n - 1) + Fibonacci(n - 2);
}

#endif  // FILE_FIBONACCI_HPP
