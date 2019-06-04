class Constants(object):

    NavigationStatus = [  # Table 7.
        'Under way using engine',
        'At anchor',
        'Not under command',
        'Restricted manoeuverability',
        'Constrained by her draught',
        'Moored',
        'Aground',
        'Engaged in Fishing',
        'Under way sailing',
        'Reserved for future amendment of Navigational Status for HSC',
        'Reserved for future amendment of Navigational Status for WIG',
        'Reserved for future use',
        'Reserved for future use',
        'Reserved for future use',
        'AIS-SART is active',
        'Not defined (default)',
    ]

    ManeuverIndicator = [  # Table 8.
        'Not available (default)',
        'No special maneuver',
        'Special maneuver (such as regional passing arrangement)',
    ]

    BlueSign = [  # Table 9.
        'No',
        'Yes',
    ]

    EPFDFixTypes = [  # Table 10.
        'Undefined (default)',
        'GPS',
        'GLONASS',
        'Combined GPS/GLONASS',
        'Loran-C',
        'Chayka',
        'Integrated navigation system',
        'Surveyed',
        'Galileo',
    ]
