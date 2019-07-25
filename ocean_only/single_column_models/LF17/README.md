# Single Column Model Runs

- These runs are from Li and Fox-Kemper (2017) JPO.
- LES solutions exist for each of these scenarios.

## Directory structure

```
.
|-- LF17
    |-- HF-25_WS-5  (Heat Flux  25 W/m2, WS = 5 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-50_WS-5  (Heat Flux  50 W/m2, WS = 5 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m5_WS-5  (Heat Flux -5 W/m2, WS = 5 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m5_WS-8  (Heat Flux -5 W/m2, WS = 8 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m5_WS-10 (Heat Flux -5 W/m2, WS = 10 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m10_WS-5 (Heat Flux -5 W/m2, WS = 5 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m25_WS-5  (Heat Flux -25 W/m2, WS = 5 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m25_WS-8  (Heat Flux -25 W/m2, WS = 8 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m25_WS-10 (Heat Flux -25 W/m2, WS = 10 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m50_WS-5  (Heat Flux -50 W/m2, WS = 5 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m50_WS-8  (Heat Flux -50 W/m2, WS = 8 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m50_WS-10 (Heat Flux -50 W/m2, WS = 10 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m100_WS-5 (Heat Flux -100 W/m2, WS = 5 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m200_WS-5 (Heat Flux -200 W/m2, WS = 5 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    |-- HF-m300_WS-5 (Heat Flux -300 W/m2, WS = 5 m/s)
    |   |-- no_waves
    |   |   |-- ePBL-OM4
    |   |   |-- ePBL-RH18
    |   |   |-- ePBL-RL19
    |   |   |-- KPP_CVMix
    |   |   `-- KPP_CVMix-LTLF17
    |   `-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
    |       |-- ePBL-OM4
    |       |-- ePBL-RH18
    |       |-- ePBL-RL19
    |       |-- KPP_CVMix
    |       `-- KPP_CVMix-LTLF17
    `-- HF-m500_WS-5 (Heat Flux -500 W/m2, WS = 5 m/s)
	|-- no_waves
	|   |-- ePBL-OM4
	|   |-- ePBL-RH18
	|   |-- ePBL-RL19
	|   |-- KPP_CVMix
	|   `-- KPP_CVMix-LTLF17
	`-- DHH85_waveage-NNN {for NNN in [0p6,0p8,1p0,1p2]
	    |-- ePBL-OM4
	    |-- ePBL-RH18
	    |-- ePBL-RL19
	    |-- KPP_CVMix
	    `-- KPP_CVMix-LTLF17
```
