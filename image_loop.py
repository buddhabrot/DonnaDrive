import os, time, pickle
from subprocess import call
DEBUG_MODE = False
IMAGES_DIR = os.path.dirname(os.path.realpath(__file__)) + '/images'
MAX_TIME = 280
SLEEP_TIME = 10
LOG_FILE = os.path.dirname(os.path.realpath(__file__)) + '/donnadrive.log'

LOG = {}

def open_log():
	global LOG
	if os.path.isfile(LOG_FILE):
		f = open(LOG_FILE)
		try:
			LOG = pickle.load(f)
		except EOFError as err:
			pass
		f.close()

def save_log():
	f = open(LOG_FILE, 'wb')
	pickle.dump(LOG, f)
	f.close()

def show_image(file, Debug = False):
	if Debug:
		print('Showing image {0}'.format(file))
	else:
		try:
			os.system("sudo killall fbi")
			os.system("sudo fbi --blend 1 --noverbose -T 1 -a '{0}' 2> /dev/null".format(file))
		except OSError as e:
			print('Could not call fbi')

	if file in LOG:
		LOG[file] += 1
	else:
		LOG[file] = 1
	save_log()

def list_images():
	path = IMAGES_DIR
	name_list = os.listdir(path)
	full_list = [os.path.join(path,i) for i in name_list]
	time_sorted_list = sorted(full_list, key=os.path.getmtime)

	return time_sorted_list

def main():
	open_log()
	t = time.time()
	while (time.time() - t) < MAX_TIME:
		file_to_show = None

		for image in list_images():
			if image not in LOG:
				file_to_show = image
				break

		for key in LOG.keys():
			if not os.path.isfile(key):
				del LOG[key]

		if not file_to_show:
			file_to_show = min(LOG, key=LOG.get)

		show_image(file_to_show, Debug=DEBUG_MODE)
		if not DEBUG_MODE:
			time.sleep(SLEEP_TIME)

if __name__ == '__main__':
	main()