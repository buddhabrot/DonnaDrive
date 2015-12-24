import os, time, pickle

DEBUG_MODE = True
IMAGES_DIR = 'images'
MAX_TIME = 300
SLEEP_TIME = 5
LOG_FILE = 'donnadrive.log'

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

		if not file_to_show:
			file_to_show = min(LOG, key=LOG.get)

		show_image(file_to_show, Debug=DEBUG_MODE)
		if not DEBUG_MODE:
			time.sleep(SLEEP_TIME)

if __name__ == '__main__':
	main()