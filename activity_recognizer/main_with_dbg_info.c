/**
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2022 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

#include "peripherals.h"
#include "reg_map.h"

#include <stdint.h>
#include <stdbool.h>

#define GYR_SENS 0.07f
#define ACC_SENS 0.244f

#define SENSOR_NUM_AXES 6
#define SENSOR_ODR 104
#define WIN_LEN_IN_SEC 1
#define WIN_LEN_IN_SAMPLES (SENSOR_ODR * WIN_LEN_IN_SEC)
#define BUF_SIZE (SENSOR_NUM_AXES * WIN_LEN_IN_SAMPLES)

void __attribute__((signal)) algo_00_init(void);
void __attribute__((signal)) algo_00(void);
// user defined function
void reset_status(void);

static volatile uint32_t int_status;

static uint32_t win_count;
static float acc_norm_sqred;
static float gyro_norm_sqred;
static float a_x_k;
static float a_x_ex;
static float a_x_ex2;

void __attribute__((signal)) algo_00_init(void)
{
	reset_status();
	// TODO: initialize algorithm
}

// reset window counter and accumulators
void reset_status(void)
{
	win_count = 0;
	for (uint8_t ax = 0; ax < SENSOR_NUM_AXES / 2 + 2; ax++)
	{
		gyro_norm_sqred = 0;
		acc_norm_sqred = 0;
	}
	a_x_k = 0.0f;
	a_x_ex = 0.0f;
	a_x_ex2 = 0.0f;
}

void __attribute__((signal)) algo_00(void)
{
	win_count++;
	float a_x = (float)cast_sint16_t(ISPU_ARAW_X) * ACC_SENS;
	float a_y = (float)cast_sint16_t(ISPU_ARAW_Y) * ACC_SENS;
	float a_z = (float)cast_sint16_t(ISPU_ARAW_Z) * ACC_SENS;
	float g_x = (float)cast_sint16_t(ISPU_GRAW_X) * GYR_SENS;
	float g_y = (float)cast_sint16_t(ISPU_GRAW_Y) * GYR_SENS;
	float g_z = (float)cast_sint16_t(ISPU_GRAW_Z) * GYR_SENS;
	float a_norm_sqred = a_x * a_x + a_y * a_y + a_z * a_z;
	float g_norm_sqred = g_x * g_x + g_y * g_y + g_z * g_z;
	//calculate norm mean
	acc_norm_sqred  += (a_norm_sqred - acc_norm_sqred) / win_count;
	gyro_norm_sqred += (g_norm_sqred - gyro_norm_sqred) / win_count;

	//setup variance acc_x
	if (win_count == 1)
	{
		a_x_k = a_x;
	}
	a_x_ex += a_x - a_x_k;
	a_x_ex2 += (a_x - a_x_k) * (a_x - a_x_k);

	int16_t prediction = -1;

	if (win_count == WIN_LEN_IN_SAMPLES)
	{
		float var_a_x = (a_x_ex2 - (a_x_ex * a_x_ex) / win_count) / (win_count - 1);

		if (acc_norm_sqred <= 3085268.25f)
		{
			if (gyro_norm_sqred <= 6889.0322f)
			{
				if (var_a_x <= 6461.0833f)
				{
					prediction = 1;
				}
				else
				{ // if var_A_X [mg] > 6461.0833f
					prediction = 4;
				}
			}
			else
			{ // if gyro_norm > 6889.0322f
				prediction = 2;
			}
		}
		else
		{ // if acc_norm > 3085268.25f
			prediction = 3;
		}

		cast_sint16_t(ISPU_DOUT_00) = prediction;
		cast_float(ISPU_DOUT_01) = var_a_x;
		cast_float(ISPU_DOUT_03) = acc_norm_sqred;
		cast_float(ISPU_DOUT_05) = gyro_norm_sqred;
		cast_float(ISPU_DOUT_07) = g_x;
		cast_float(ISPU_DOUT_09) = a_x;

		reset_status();
	}
	// TODO: read and process sensor data

	// interrupt generation (set bit 0 for algo 0, bit 1 for algo 1, etc.)
	int_status = int_status | 0x1u;
}

// For more algorithms implement the corresponding functions: algo_01_init and
// algo_01 for algo 1, algo_02_init and algo_02 for algo 2, etc.

int main(void)
{
	// set boot done flag
	uint8_t status = cast_uint8_t(ISPU_STATUS);
	status = status | 0x04u;
	cast_uint8_t(ISPU_STATUS) = status;

	// enable algorithms interrupt request generation
	cast_uint8_t(ISPU_GLB_CALL_EN) = 0x01u;

	while (true)
	{
		stop_and_wait_start_pulse;

		// reset status registers and interrupts
		int_status = 0u;
		cast_uint32_t(ISPU_INT_STATUS) = 0u;
		cast_uint8_t(ISPU_INT_PIN) = 0u;

		// get all the algorithms to run in this time slot
		cast_uint32_t(ISPU_CALL_EN) = cast_uint32_t(ISPU_ALGO) << 1;

		// wait for all algorithms execution
		while (cast_uint32_t(ISPU_CALL_EN) != 0u)
		{
		}

		// get interrupt flags
		uint8_t int_pin = 0u;
		int_pin |= ((int_status & cast_uint32_t(ISPU_INT1_CTRL)) > 0u) ? 0x01u : 0x00u;
		int_pin |= ((int_status & cast_uint32_t(ISPU_INT2_CTRL)) > 0u) ? 0x02u : 0x00u;

		// set status registers and generate interrupts
		cast_uint32_t(ISPU_INT_STATUS) = int_status;
		cast_uint8_t(ISPU_INT_PIN) = int_pin;
	}
}
