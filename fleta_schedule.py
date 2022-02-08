#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.07.29
    @author: jhbae
'''
import sys

from lib.srm_schedule import SrmSchedule

if __name__ == '__main__':
    if len(sys.argv) > 1:
        srm_schedule = SrmSchedule()
        srm_schedule.main()
