#!/usr/bin/env python3
import influxdb
import json
import urllib.request

import localsettings as settings


influx = influxdb.InfluxDBClient(host=settings.influxdb["hostname"], database=settings.influxdb["database"])

for source in settings.issues:
	url = "https://sentry.io/api/0/issues/{0[issue_id]}/events/".format(source)
	auth = "Bearer {0[authorization_token]}".format(source)
	if source["tags"] == ["ALL"]:
		matches_tag = lambda x: True
	else:
		source_tags = set(source["tags"])
		matches_tag = lambda t: t in source_tags

	request = urllib.request.Request(url, headers={"Authorization": auth})
	with urllib.request.urlopen(request) as data:
		sentry_data = json.loads(data.read().decode('utf-8'))
		influx_data = []
		for event in sentry_data:
			date = event["dateCreated"]
			tags = {t["key"]: t["value"] for t in event["tags"]
			        if matches_tag(t["key"])}
			influx_data.append({
				"time": date,
				"measurement": source["name"],
				"tags": tags,
				"fields": {"count": 1}
			})
		influx.write_points(influx_data, time_precision='s')
