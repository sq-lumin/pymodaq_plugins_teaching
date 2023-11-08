# -*- coding: utf-8 -*-
"""
Created the 08/11/2023

@author: Sebastien Weber
"""

from pymodaq.utils.enums import BaseEnum

SerialAddresses = BaseEnum('SerialAdresses', ['GPIB::16', 'USB::120x::RAW', 'COM7'])

