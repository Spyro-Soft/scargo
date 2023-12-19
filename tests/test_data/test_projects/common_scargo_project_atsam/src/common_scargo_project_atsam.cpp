/**
 * @copyright Copyright (C) 2023 <Company-Name>. All rights reserved.
 */

#include <cstdio>
#if ATSAM
#include <sam.h>
#endif  // ATSAM
#ifndef ESP32
/**
 * @brief This is example function doc
 *
 * @return int 0 if all good
 */
int main()
{
#if defined STM32 || defined ATSAM
    while (true)
    {
    }
#endif  // STM32 || ATSAM
    return 0;
}
#endif  // !ESP32
