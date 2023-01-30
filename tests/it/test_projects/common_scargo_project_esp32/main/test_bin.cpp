//
// Copyright
//

#include <cstdio>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <esp_log.h>

extern "C"
{
    void app_main(void);
}

/**
 * @brief Main freeRTOS task
 *
 */
void app_main(void)
{
    for (;;)
    {
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
