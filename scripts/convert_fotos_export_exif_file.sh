#!/bin/bash

exiftool "-FileCreateDate<DateTimeOriginal" "-FileModifyDate<DateTimeOriginal" *
