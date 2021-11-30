#!/usr/bin/env bash
source venv/bin/activate

echo "test review apis"
echo "================"
pytest app/test/apis/review.py --capture=sys

echo "test comment apis"
echo "================"
pytest app/test/apis/comment.py --capture=sys

echo "test qna apis"
echo "================"
pytest app/test/apis/qna.py --capture=sys
