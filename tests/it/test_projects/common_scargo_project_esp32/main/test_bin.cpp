//
// Copyright
//

#include <cstdio>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <esp_log.h>

extern "C"
{
    void appMain(void);
}

/**
 * @brief Main freeRTOS task
 *
 */
void appMain(void)
{
    for (;;)
    {
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
