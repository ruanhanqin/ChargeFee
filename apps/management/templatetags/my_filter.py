#!/usr/bin/env python
# -*-encoding: utf-8-*-

from django import template

register = template.Library()


@register.filter
def filter_str(val):
    return val.replace('山西省阳泉市平定县冠山镇', '')
