import write
import auxil
import consts
import change_case

from random import choice, randint
import argparse
from os import makedirs, listdir
import re
from time import time
import json

from loguru import logger

def load_samples(samples_dir):
	with open(samples_dir + "/headers.txt") as headerfile:
		header = headerfile.read().split(";;\n")

	with open(samples_dir + "/names.txt") as namefile:
		name = namefile.read().split(";;\n")

	with open(samples_dir + "/intros.txt") as introfile:
		intro = introfile.read().split(";;\n")

	with open(samples_dir + "/instructions.json") as instructionfile:
		instructions = json.load(instructionfile)

	with open(samples_dir + "/execution_control.txt") as execution_controlfile:
		execution_control = execution_controlfile.read().split('\n')

	with open(samples_dir + "/responsible.json") as responsiblefile:
		responsible = json.load(responsiblefile)

	with open(samples_dir + "/creators.txt") as creatorfile:
		creator = creatorfile.read().split('\n')

	logo_list = listdir(samples_dir+"/logo")
	sign_list = listdir(samples_dir+"/signature")
	seal_list = listdir(samples_dir+"/seal")
		
	logger.debug(f"[header] length: {len(header)}")
	logger.debug(f"[name] length: {len(name)}")
	logger.debug(f"[intro] length: {len(intro)}")
	logger.debug(f"[instructions] length: {len(instructions)}")
	logger.debug(f"[execution_control] length: {len(execution_control)}")
	logger.debug(f"[responsible] length: {len(responsible)}")
	logger.debug(f"[creator] length: {len(creator)}")

	return (header, name, intro, instructions, execution_control, responsible,
		creator, logo_list, sign_list, seal_list)

def generate(data, out, formats, size, samples_dir, is_image):
	logger.info(f"Using formats: {formats}")

	try:
		makedirs(out+"/json")
		if 'd' in formats:
			makedirs(out+"/docx")
		if 'p' in formats:
			makedirs(out+"/pdf")
		if 'j' in formats:
			makedirs(out+"/jpg")
	except FileExistsError:
		pass

	measure_time = 1
	count = 0
	start = time()
	json_path = write.create_COCO_json(data, out)
	while True:
		header = choice(data[0])
		name = choice(data[1])
		intro = choice(data[2])
		
		all_instructions = data[3]
		instruction = []

		for _ in range(randint(1, 7)):
			instruction.append(choice(all_instructions))

		# Удаление повторяющихся элементов
		i = []
		for e in instruction:
			if e not in i:
				i.append(e)
		instruction = i

		execution_control = choice(data[4])

		# Шанс 33% на наличие ответственных в приказе
		if randint(1, 3) == 1:
			responsible_arr = choice(data[5])
			responsible = change_case.create_responsible(execution_control, responsible_arr[0])
			responsible_arr[0] = responsible
		else:
			responsible = ""
			responsible_arr = []

		creator = choice(data[6])
		date = auxil.generate_date(unixtime=True)

		if is_image:
			logo = samples_dir + "logo/" + choice(data[7])
			sign = samples_dir + "signature/" + choice(data[8])
			seal = samples_dir + "seal/" + choice(data[9])
		else:
			logo, sign, seal = None, None, None

		instruction = write.extend_instruction(instruction, samples_dir)

		 #write.write_json(instruction, responsible_arr, date, out, count)

		if 'd' in formats:
			docx_path = write.write_docx(header, name, intro, instruction,
				responsible, creator, date[0], out, count, logo, sign, seal)

		if 'p' in formats:
			pdf_path = write.write_pdf_linux(docx_path, out, count)

			generation_data = (header, name, intro, instruction,
				responsible, creator, date[0])
			
			if is_image:
				write.write_to_COCO_json(json_path, pdf_path, generation_data, is_image = True)
			else:
				write.write_to_COCO_json(json_path, pdf_path, generation_data)

		if 'j' in formats:
			write.write_jpg(out, count)

		count += 1
		if auxil.getsize(out) >= size:
			logger.warning(f"Size of {out} dir: {auxil.getsize(out)} bytes")
			break

		if measure_time:
			if count % 100 == 0:
				avg_speed = auxil.getsize(out) / (time()-start)
				full_time = round((size) / (avg_speed*60), 2)
				measure_time = 0
				if full_time < 1:
					logger.warning("Approximate generation time: "
								  f"{round(full_time*60, 2)} s.")
				else:
					logger.warning("Approximate generation time: "
								  f"{full_time} min.")


def get_args():
	parser = argparse.ArgumentParser(
		description="Decrees generator",
		epilog="Example: python3 gen.py 50MB -f dp -s samples -o decrees -vv")

	parser.add_argument("size", help="Max size of output dir. For example: 10KB, 10MB, 10GB",
						type=auxil.check_size_format)
	parser.add_argument("-i", "--image", help="use images (logo, signature, seal) in decree",
						action="store_true")
	parser.add_argument("-f", "--format", help="formats to save (docx: d, pdf: p, jpg: j)",
						type=auxil.parse_formats, default="dp", metavar="format")
	parser.add_argument("-s", "--samples", help="path to dir with samples",
						metavar="path", type=str, default="./samples/")
	parser.add_argument("-o", "--out", help="path for output files",
						metavar="path", type=str, default="./decrees")
	parser.add_argument("-v", "--verbose", action="count", default=0,
						help="verbose output")

	return parser.parse_args()

def main():
	global args

	args = get_args()
	auxil.logger_config(args.verbose)

	data = load_samples(args.samples)
	bytes_size = auxil.size_to_bytes(args.size)

	logger.warning("Generation is started...")
	generate(data, args.out, args.format, bytes_size, args.samples, args.image)
	logger.warning("Generation is finished!")

if __name__ == '__main__':
	main()
