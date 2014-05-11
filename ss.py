#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Contributors: gdestuynder@mozilla.com

import requests

API_KEY=""
API_URL="https://api.smartsheet.com/1.1"
DISPLAY_FINISHED_TASKS = False

# RST style header
def print_hdr(hdr):
	print(hdr)
	print('=' * len(hdr))

# CONTACT_LIST == assignee
def belongs_to_user(row, user):
	for cell in row['cells']:
		if cell['type'] == 'CONTACT_LIST' and cell['value'] == user['email']:
			return True
	return False

# That's where most of the hackery happens.
# TEXT_NUMBER can be anything as the name implies.
# CHECKBOX are used for tasks only, when checked it means the task is completed.
def get_text_values(row):
	r = []
	for cell in row['cells']:
		v = None
		if cell['type'] == 'CHECKBOX':
			if cell['value']:
				r.append('100%')
				if not DISPLAY_FINISHED_TASKS:
					return None
				continue

		if cell['type'] == 'TEXT_NUMBER':
			try:
				v = cell['displayValue']
			except (AttributeError, KeyError):
				continue
		if v == None: continue
		try:
			v = int(v)
			continue
		except:
			pass
		r.append(v)

	ret = {'name': r[0], 'state': '0%', 'comment': ''}
	r.pop(0)
	for x in r:
		if x.find('%') != -1:
			ret['state'] = x
			continue
		ret['comment'] = x

	if not DISPLAY_FINISHED_TASKS and ret['state'] == '100%':
		return None
	return ret

def runcmd(path):
	ret = requests.get(API_URL+path, headers={'Authorization': 'Bearer '+API_KEY})	
	return ret.json()

def main():
	user = runcmd('/user/me')
	sheets = runcmd('/sheets')

	for i in sheets:
		sheet = runcmd('/sheet/'+str(i['id']))
		print_hdr(sheet['name'])
		for row in sheet['rows']:
			if belongs_to_user(row, user):
				r = get_text_values(row)
				if r != None:
					print(r['state']+': '+r['name'])

if __name__ == '__main__':
	main()
