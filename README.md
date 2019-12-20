# Python port for ITE keyboard leds utility

This utility can be used for ITE mechanical keyboard with per-key led:

      $ lsusb | grep 048d:ce00
      Bus 001 Device 003: ID 048d:ce00 Integrated Technology Express, Inc. ITE Device(8291)


### Setup (python 3)

      $ pip install hidapi colour
      $ chmod a+x ite-keyboard.py


### Usage

      $ sudo ite-keyboard.py
      usage: ite-keyboard [cmd] [args]
      where 'cmd' and 'args' can be:
        mode [off | fade | wave | dots | rainbow | explosion | snake | raindrops]
        color [rows range] [columns range] [color name]

      Column and row ranges can be expressed as:
       - single value:         3            row #3
       - list of values:       0,2,4        rows 0, 2 and 4
       - range of values:      5-17         columns from 5 to 17
       - mixed list and range: 0-2,17,18    columns 0, 1, 2, 17 and 18
       - all possible values:  all          rows from 0 to 5 and columns from 0 to 20

      Some examples:
      # ite-keyboard mode snake                         starts snake mode
      # ite-keyboard color 0 all yellow                 yellow on row #0 keys
      # ite-keyboard color 0,5 all red 2-4 all white    red on rows 0 and 5 and white on rows 2 to 4
      # ite-keyboard color 1,4-5 0-1,18-19 blue         blue for the first and
                                                        last 2 keys of rows 1, 4 and 5
      # ite-keyboard color all all green                full green keyboard

