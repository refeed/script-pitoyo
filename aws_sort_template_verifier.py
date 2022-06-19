TEMPLATE_VERIFIER = {
    'SANITY_CHECK': [
        (1, 'begin( product )\n'),
        (201, 'end( product )\n'),

        (66, '            Name : ARG Jerowaru\n'),
        (79, '               ID : rain_total\n'),
        (80, '               Description : Total Rain\n'),

        (89, '            Name : ARG Mataram\n'),
        (89+13, '               ID : rain_total\n'),
        (89+14, '               Description : Total Rain\n'),

        (112, '            Name : ARG Pemenang\n'),
        (112+13, '               ID : rain_total\n'),
        (112+14, '               Description : Total Rain\n'),

        (135, '            Name : ARG Praya\n'),
        (135+13, '               ID : rain_total\n'),
        (135+14, '               Description : Total Rain\n'),

        (158, '            Name : ARG Sekotong\n'),
        (158+13, '               ID : rain_total\n'),
        (158+14, '               Description : Total Rain\n'),

        (181, '            Name : ARG Selong\n'),
        (181+13, '               ID : rain_total\n'),
        (181+14, '               Description : Total Rain\n'),
    ],
}

RAIN_TOTAL_LINE_LOCATION = {
    'ARG Jerowaru': 80+1,
    'ARG Mataram': 89+14+1,
    'ARG Pemenang': 112+14+1,
    'ARG Praya': 135+14+1,
    'ARG Sekotong': 158+14+1,
    'ARG Selong': 181+14+1,
}
