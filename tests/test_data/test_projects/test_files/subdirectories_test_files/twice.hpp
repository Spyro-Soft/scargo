//
// Copyright
//

#pragma once

#ifndef FILE_TWICE_HPP
#define FILE_TWICE_HPP

template <typename T>
T twice(const T& value)
{
    return value * static_cast<T>(2);
}

#endif  // FILE_TWICE_HPP
