#!/usr/bin/env bash

echo "test review apis"
echo "================"
pytest app/test/apis/review.py --capture=sys

echo "test comment apis"
echo "================"
pytest app/test/apis/comment.py --capture=sys
