# Hồ sơ dữ liệu giai đoạn O

Sinh bởi `scripts.report_data_profile`.

Chỉ đọc manifest/split/annotation đã đóng băng. Không đọc prediction hoặc audio. Thống kê test là mô tả dữ liệu, không dùng chọn hệ thống hoặc suy prior.

Lưới thời gian: t=0,0.1,…<duration, event hoạt động khi onset ≤ t < offset. Đếm số event, kể cả event cùng lớp. Gap có dấu: onset kế − offset trước; giữ số âm khi chồng lấn. Cửa sổ train: ceil(duration/10), không bỏ GT thiếu.

## Độ dài recording theo split (giây)

| Split | N | Mean | Quantile |
| --- | --- | --- | --- |
| test | 142 | 87.85569799750887 | {'0': 2.2932879818594105, '0.05': 15.265814058956918, '0.25': 32.13772108843537, '0.5': 70.27594104308389, '0.75': 113.84385487528344, '0.95': 205.90563492063492, '1': 701.7923129251701} |
| train | 438 | 93.35023022603256 | {'0': 3.358730158730159, '0.05': 12.683384353741497, '0.25': 31.951780045351473, '0.5': 80.69761904761904, '0.75': 126.78064058956917, '0.95': 219.45791383219927, '1': 818.3189342403629} |
| validation | 137 | 101.47462121588296 | {'0': 5.474988662131519, '0.05': 15.16, '0.25': 35.02886621315193, '0.5': 95.52938775510204, '0.75': 141.63702947845806, '0.95': 196.4296825396825, '1': 714.5477551020408} |

## Event polyphonic theo lớp × split

| Split | Lớp | N | Median s | % <1s |
| --- | --- | --- | --- | --- |
| test | bells | 28 | 3.6399999999999997 | 3.571428571428571 |
| test | birds | 29 | 8.36999999999999 | 6.896551724137931 |
| test | cat_fights_and_moans | 9 | 2.870000000000001 | 0.0 |
| test | chicken_coop | 34 | 2.5249999999999986 | 0.0 |
| test | cicadas_and_crickets | 70 | 4.095 | 1.4285714285714286 |
| test | crows_seagulls_magpies | 24 | 3.1599999999999993 | 0.0 |
| test | dog_barkings_and_howlings | 39 | 2.289999999999992 | 17.94871794871795 |
| test | glass_breaking | 31 | 3.8999999999999986 | 9.67741935483871 |
| test | horn | 30 | 1.3950000000000022 | 26.666666666666668 |
| test | jet_aircrafts | 15 | 31.590000000000003 | 0.0 |
| test | lawn_mower_brush_cutter_olive_shaker | 35 | 20.57 | 2.857142857142857 |
| test | music | 36 | 12.215 | 0.0 |
| test | propeller_aircrafts | 26 | 32.405 | 0.0 |
| test | sirens_and_alarms | 25 | 14.45 | 4.0 |
| test | thunder_fireworks_gunshot | 32 | 3.235000000000003 | 0.0 |
| test | train | 28 | 25.010000000000005 | 0.0 |
| test | vacuum_cleaner_fan_hairdryer | 17 | 13.070000000000007 | 0.0 |
| test | vehicle_idling | 33 | 9.0 | 0.0 |
| test | vehicle_pass_by | 70 | 8.045000000000002 | 0.0 |
| test | voices | 60 | 2.114999999999999 | 15.0 |
| test | workshop | 69 | 5.719999999999999 | 0.0 |
| train | bells | 62 | 8.36 | 0.0 |
| train | birds | 151 | 4.210000000000008 | 3.9735099337748347 |
| train | cat_fights_and_moans | 89 | 1.9699999999999989 | 0.0 |
| train | chicken_coop | 108 | 2.16 | 4.62962962962963 |
| train | cicadas_and_crickets | 240 | 5.195 | 0.8333333333333334 |
| train | crows_seagulls_magpies | 108 | 2.6950000000000003 | 12.962962962962962 |
| train | dog_barkings_and_howlings | 144 | 2.3049999999999997 | 11.805555555555555 |
| train | glass_breaking | 72 | 1.964999999999998 | 6.944444444444445 |
| train | horn | 88 | 1.5 | 26.136363636363637 |
| train | jet_aircrafts | 55 | 20.450000000000003 | 0.0 |
| train | lawn_mower_brush_cutter_olive_shaker | 72 | 14.254999999999981 | 0.0 |
| train | music | 80 | 15.695 | 0.0 |
| train | propeller_aircrafts | 78 | 38.010000000000005 | 0.0 |
| train | sirens_and_alarms | 81 | 11.48 | 0.0 |
| train | thunder_fireworks_gunshot | 79 | 3.09 | 3.79746835443038 |
| train | train | 81 | 24.49 | 0.0 |
| train | vacuum_cleaner_fan_hairdryer | 86 | 16.775 | 0.0 |
| train | vehicle_idling | 91 | 12.190000000000001 | 0.0 |
| train | vehicle_pass_by | 157 | 7.920000000000002 | 0.0 |
| train | voices | 222 | 2.434999999999995 | 15.765765765765765 |
| train | workshop | 264 | 9.059999999999999 | 0.7575757575757576 |
| validation | bells | 26 | 2.6500000000000004 | 0.0 |
| validation | birds | 87 | 3.4099999999999984 | 3.4482758620689653 |
| validation | cat_fights_and_moans | 40 | 4.695 | 0.0 |
| validation | chicken_coop | 24 | 2.2700000000000005 | 0.0 |
| validation | cicadas_and_crickets | 109 | 4.719999999999999 | 0.0 |
| validation | crows_seagulls_magpies | 28 | 1.0000000000000002 | 42.857142857142854 |
| validation | dog_barkings_and_howlings | 88 | 1.8800000000000097 | 11.363636363636363 |
| validation | glass_breaking | 17 | 2.4399999999999977 | 11.76470588235294 |
| validation | horn | 21 | 2.3599999999999994 | 23.809523809523807 |
| validation | jet_aircrafts | 17 | 31.04 | 0.0 |
| validation | lawn_mower_brush_cutter_olive_shaker | 28 | 6.135 | 0.0 |
| validation | music | 26 | 23.64 | 0.0 |
| validation | propeller_aircrafts | 21 | 26.860000000000003 | 0.0 |
| validation | sirens_and_alarms | 23 | 11.41 | 0.0 |
| validation | thunder_fireworks_gunshot | 18 | 9.095 | 0.0 |
| validation | train | 24 | 25.270000000000003 | 0.0 |
| validation | vacuum_cleaner_fan_hairdryer | 30 | 17.105 | 0.0 |
| validation | vehicle_idling | 28 | 11.145 | 0.0 |
| validation | vehicle_pass_by | 60 | 10.550000000000004 | 0.0 |
| validation | voices | 77 | 1.3499999999999979 | 22.07792207792208 |
| validation | workshop | 94 | 10.079999999999998 | 0.0 |

## Độ phủ trên lưới 0.1 s

| Split | Số điểm | 0 / 1 / 2 / ≥3 |
| --- | --- | --- |
| test | 124818 | [0.2641205595346825, 0.6740454101171306, 0.06057619894566489, 0.0012578314025220722] |
| train | 409094 | [0.31052276493910935, 0.6530528436007372, 0.03554439810899206, 0.0008799933511613468] |
| validation | 139088 | [0.31464971816404, 0.6192841941792246, 0.05858161739330496, 0.007484470263430346] |

## Thiếu GT polyphonic

| Split | Recording | Mono theo lớp |
| --- | --- | --- |
| test | ['S-0711', 'S-0716', 'S-0717'] | {'wind_turbine': 25, 'crows_seagulls_magpies': 7, 'chicken_coop': 7, 'workshop': 3, 'vehicle_pass_by': 2, 'birds': 2, 'thunder_fireworks_gunshot': 1, 'horn': 1} |
| train | ['S-0704', 'S-0705', 'S-0707', 'S-0709', 'S-0710', 'S-0712', 'S-0713', 'S-0715'] | {'wind_turbine': 55, 'vehicle_pass_by': 12, 'vehicle_idling': 11, 'workshop': 7, 'jet_aircrafts': 7, 'music': 4, 'thunder_fireworks_gunshot': 2, 'propeller_aircrafts': 2, 'crows_seagulls_magpies': 2, 'voices': 1, 'birds': 1} |
| validation | ['S-0706', 'S-0708', 'S-0714'] | {'wind_turbine': 33, 'thunder_fireworks_gunshot': 12, 'vehicle_pass_by': 7, 'workshop': 4, 'crows_seagulls_magpies': 3, 'vehicle_idling': 2, 'vacuum_cleaner_fan_hairdryer': 2} |

## Recording giống byte

| Trái | Phải | Split trái | Split phải |
| --- | --- | --- | --- |
| S-0569 | S-0572 | train | train |
| S-0397 | S-0585 | train | train |
| S-0621 | S-0623 | validation | validation |
| S-0108 | S-0589 | train | train |
| S-0062 | S-0198 | test | test |
| S-0570 | S-0571 | validation | validation |
| S-0289 | S-0500 | train | train |
| S-0606 | S-0622 | validation | validation |

## Mono vs poly theo lớp

| Lớp | Poly | Mono |
| --- | --- | --- |
| bells | 116 | 123 |
| birds | 267 | 225 |
| cat_fights_and_moans | 138 | 138 |
| chicken_coop | 166 | 169 |
| cicadas_and_crickets | 419 | 421 |
| crows_seagulls_magpies | 160 | 166 |
| dog_barkings_and_howlings | 271 | 240 |
| glass_breaking | 120 | 121 |
| horn | 139 | 133 |
| jet_aircrafts | 87 | 99 |
| lawn_mower_brush_cutter_olive_shaker | 135 | 140 |
| music | 142 | 160 |
| propeller_aircrafts | 125 | 217 |
| sirens_and_alarms | 129 | 148 |
| thunder_fireworks_gunshot | 129 | 145 |
| train | 133 | 156 |
| vacuum_cleaner_fan_hairdryer | 133 | 136 |
| vehicle_idling | 152 | 159 |
| vehicle_pass_by | 287 | 318 |
| voices | 359 | 343 |
| wind_turbine | 0 | 113 |
| workshop | 427 | 439 |

## DataSEC v3 theo lớp (giây)

| Lớp | N | Median | Min | Max |
| --- | --- | --- | --- | --- |
| bells | 67 | 29.63700680272109 | 2.71281179138322 | 73.07863945578231 |
| birds | 69 | 5.0 | 1.9742857142857144 | 79.97496598639455 |
| cat_fights_and_moans | 50 | 19.970646258503404 | 2.3920408163265305 | 66.97412698412698 |
| chicken_coop | 58 | 11.30360544217687 | 0.9810884353741496 | 55.14383219954649 |
| cicadas_and_crickets | 74 | 18.198356009070295 | 4.219863945578231 | 77.36945578231293 |
| crows_seagulls_magpies | 106 | 22.745396825396824 | 1.5488662131519275 | 198.3654648526077 |
| dog_barkings_and_howlings | 70 | 7.563401360544217 | 0.3537414965986394 | 37.74199546485261 |
| glass_breaking | 109 | 60.52374149659864 | 0.2376190476190476 | 60.52507936507936 |
| horn | 57 | 1.87843537414966 | 0.2945804988662131 | 45.200362811791386 |
| jet_aircrafts | 103 | 24.90746031746032 | 7.145396825396825 | 87.28126984126985 |
| lawn_mower_brush_cutter_olive_shaker | 127 | 38.4018820861678 | 7.233582766439909 | 248.8714058956916 |
| music | 1001 | 30.00018140589569 | 10.0 | 30.648888888888887 |
| propeller_aircrafts | 108 | 22.041145124716554 | 5.0422902494331066 | 228.13632653061225 |
| sirens_and_alarms | 105 | 10.382585034013603 | 1.91297052154195 | 99.06904761904762 |
| thunder_fireworks_gunshot | 235 | 2.0 | 0.429501133786848 | 174.60907029478457 |
| train | 67 | 19.381927437641725 | 3.886757369614513 | 230.1384126984127 |
| vacuum_cleaner_fan_hairdryer | 95 | 23.45877551020408 | 2.661541950113379 | 301.0 |
| vehicle_idling | 112 | 23.5512925170068 | 2.353650793650793 | 481.4839002267574 |
| vehicle_pass_by | 217 | 5.268548752834467 | 1.1111111111111112 | 303.1361678004535 |
| voices | 1900 | 2.2429251700680273 | 0.2040362811791383 | 29.9437641723356 |
| wind_turbine | 100 | 10.0 | 10.0 | 59.343990929705214 |
| workshop | 218 | 19.950544217687074 | 0.600498866213152 | 233.43925170068027 |

## poly_event_duration

```json
{
  "count": 4034,
  "mean": 12.458239960337135,
  "quantiles": {
    "0": 0.41000000000000014,
    "0.05": 1.0099999999999956,
    "0.25": 2.329999999999999,
    "0.5": 5.800000000000001,
    "0.75": 14.545000000000002,
    "0.95": 43.470499999999994,
    "1": 296.5
  },
  "under_0_5s": 8,
  "under_1s": 194,
  "percent_under_1s": 4.80912245909767
}
```

## same_class_gaps

```json
{
  "count": 2693,
  "mean": 8.630958039361307,
  "quantiles": {
    "0": 0.0,
    "0.05": 0.6000000000000014,
    "0.25": 2.230000000000004,
    "0.5": 4.23,
    "0.75": 8.260000000000002,
    "0.95": 34.09800000000002,
    "1": 233.02
  },
  "under_1s": 252,
  "overlapping": 0
}
```

## gaps_by_split

```json
{
  "test": {
    "count": 468,
    "mean": 8.976645299145298,
    "quantiles": {
      "0": 0.019999999999999574,
      "0.05": 0.3135000000000016,
      "0.25": 2.12,
      "0.5": 4.210000000000002,
      "0.75": 8.372500000000002,
      "0.95": 36.44299999999999,
      "1": 233.02
    },
    "under_1s": 61,
    "overlapping": 0
  },
  "train": {
    "count": 1611,
    "mean": 8.65037864680323,
    "quantiles": {
      "0": 0.0,
      "0.05": 0.5950000000000006,
      "0.25": 2.195,
      "0.5": 4.060000000000002,
      "0.75": 8.334999999999997,
      "0.95": 34.325,
      "1": 150.13
    },
    "under_1s": 161,
    "overlapping": 0
  },
  "validation": {
    "count": 614,
    "mean": 8.316514657980456,
    "quantiles": {
      "0": 0.25,
      "0.05": 1.0,
      "0.25": 2.4224999999999985,
      "0.5": 4.519999999999996,
      "0.75": 8.14,
      "0.95": 30.571000000000055,
      "1": 131.47
    },
    "under_1s": 30,
    "overlapping": 0
  }
}
```

## datasec_duration

```json
{
  "count": 5048,
  "mean": 16.907617300221727,
  "quantiles": {
    "0": 0.2040362811791383,
    "0.05": 0.5941065759637189,
    "0.25": 2.445668934240363,
    "0.5": 8.716077097505668,
    "0.75": 30.00018140589569,
    "0.95": 49.91349433106559,
    "1": 481.4839002267574
  }
}
```

## Cửa sổ train 10 s

Tổng: 4306; top-20: 0.1658151416627961; top-5: 0.06177426846261031.

| Recording | Giây | Cửa sổ |
| --- | --- | --- |
| S-0713 | 818.3189342403629 | 82 |
| S-0715 | 659.7199319727891 | 66 |
| S-0587 | 399.2550113378685 | 40 |
| S-0712 | 396.5052154195012 | 40 |
| S-0295 | 371.24349206349206 | 38 |
| S-0710 | 367.3331292517007 | 37 |
| S-0709 | 364.4259183673469 | 37 |
| S-0208 | 352.54861678004534 | 36 |
| S-0707 | 336.26419501133785 | 34 |
| S-0705 | 328.72691609977323 | 33 |
| S-0102 | 302.91002267573697 | 31 |
| S-0704 | 290.81108843537413 | 30 |
| S-0127 | 269.17333333333335 | 27 |
| S-0305 | 267.07873015873014 | 27 |
| S-0172 | 263.4398639455782 | 27 |
| S-0097 | 262.57065759637186 | 27 |
| S-0107 | 259.47909297052155 | 26 |
| S-0322 | 255.5219274376417 | 26 |
| S-0676 | 243.0111337868481 | 25 |
| S-0239 | 242.0 | 25 |

Mono khớp khít poly (21 lớp): 3393 / 4196 event mono.

Hash từng bảng nguồn và git provenance nằm trong JSON đi kèm.
