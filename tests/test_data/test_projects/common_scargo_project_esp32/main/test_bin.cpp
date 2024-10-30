//
// Copyright
//

#include <cstdio>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <esp_log.h>

extern "C"
{
    void app_main(void);  // NOLINT(readability-identifier-naming): name required by freertos
}

/**
 * @brief Main freeRTOS task
 *
 */
// cppcheck-suppress unusedFunction
void app_main(void)  // NOLINT(readability-identifier-naming): name required by freertos
{
    for (;;)
    {
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
