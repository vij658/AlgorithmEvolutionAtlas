"""The book's eras, in order. Each era module has ERA, TOPICS, MAP and timeline_events() (see era01.py)."""
import era01
import era02
import era03
import era04

ERAS = [era01, era02, era03, era04]
BY_NUM = {e.ERA["num"]: e for e in ERAS}
