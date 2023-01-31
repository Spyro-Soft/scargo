/**
 * @copyright Copyright (C) 2021 Spyrosoft Solutions. All rights reserved.
 */

#pragma once

#include <iostream>
#include <stdexcept>

template <typename Mock>
class StaticMock
{
public:
    static inline Mock& instance()
    {
        if (nullptr == p_instance)
        {
            throw std::logic_error{"null Mock instance"};
        }
        return *p_instance;
    }
    StaticMock(const StaticMock&) = delete;
    StaticMock(StaticMock&&) = delete;
    StaticMock& operator=(const StaticMock&) = delete;
    StaticMock& operator=(StaticMock&&) = delete;

protected:
    ~StaticMock() noexcept
    {
        StaticMock::p_instance = nullptr;
    }

    static Mock* p_instance;

private:
    friend Mock;

    StaticMock() noexcept
    {
        p_instance = derived();
    }

    Mock* derived() noexcept
    {
        return static_cast<Mock*>(this);
    }
    Mock const* derived() const noexcept
    {
        return static_cast<Mock const*>(this);
    }
};

template <typename Mock>
Mock* StaticMock<Mock>::p_instance{nullptr};
