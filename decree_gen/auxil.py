import russian_datetime
import consts

import re
from sys import stdout, platform
from random import randint, choice
import os
import subprocess as sb
from argparse import ArgumentTypeError
import copy

from PyPDF2 import PdfReader
from loguru import logger

import re

import random
from PIL import Image, ImageDraw #Подключим необходимые библиотеки. 

def add_noise(path,factor):
	image = Image.open(path) #Открываем изображение. 
	draw = ImageDraw.Draw(image) #Создаем инструмент для рисования. 
	width = image.size[0] #Определяем ширину. 
	height = image.size[1] #Определяем высоту. 	
	pix = image.load() #Выгружаем значения пикселей.

	for i in range(width):
		for j in range(height):
			rand = random.randint(-factor, factor)
			a = pix[i, j][0] + rand
			b = pix[i, j][1] + rand
			c = pix[i, j][2] + rand
			if (a < 0):
				a = 0
			if (b < 0):
				b = 0
			if (c < 0):
				c = 0
			if (a > 255):
				a = 255
			if (b > 255):
				b = 255
			if (c > 255):
				c = 255
			draw.point((i, j), (a, b, c))
	del draw
	#os.remove(path)
	image.save(path) 

def logger_config(v):
	logger.remove()
	if int(v) == 0:
		logger.add(stdout, level="WARNING")
	elif int(v) == 1:
		logger.add(stdout, level="INFO")
	elif int(v) >= 2:
		logger.add(stdout, level="DEBUG")

	logger.add("logs/gen.log", level = "INFO", rotation="10 MB")

def generate_date(standart_format=False, unixtime=False):
	day = randint(1, 31)
	month = randint(1, 12)
	year = randint(2000, 2022)

	try:
		if not standart_format:
			date = russian_datetime.date(year, month, day).strftime(choice(consts.formats))
		else:
			date = russian_datetime.date(year, month, day).strftime(consts.formats[0])
	except ValueError:
		return generate_date(standart_format)

	if not unixtime:
		return date[0]
	else:
		return date

def check_size_format(size, pat=re.compile(r"^\d*[KMGB]B$")):
	if not pat.match(size):
		logger.error(f"Invalid size argument: {size}")
		raise ArgumentTypeError("Invalid value")
	return size

def size_to_bytes(size):
	s = int(size[:-2])
	if "KB" in size:
		s *= 1024
	elif "MB" in size:
		s *= 1024**2
	elif "GB" in size:
		s *= 1024**3
	elif "BB":
		s = s
	else:
		logger.error(f"Invalid size argument: {size}")

	return s

def getsize(out):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(out):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			if not os.path.islink(fp):
				total_size += os.path.getsize(fp)

	return total_size

def to_roman(n):
    result = ''
    for arabic, roman in zip((1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
                             'm     cm   d    cd   c    xc  l   xl  x   ix v  iv i'.split()):
        result += n // arabic * roman
        n %= arabic

    return result

def add_numbering(instruction):
	string_instruction = ""

	for e in instruction:
		string_instruction += e["task_text"]
		string_instruction += '\n'
	instruction = string_instruction[:-1]

	clauses = re.split(r"\{\d*\}", instruction)[1:]
	numbering_types = [choice(consts.numbering_types) for _ in range(3)]
	complete_instruction = [{"clause": clauses[0],
							"index": 1,
							"nesting_level": 0,
							"numbering_type": numbering_types[0]}]
	numbering = [1, 1, 1]

	for indx in range(1, len(clauses)):
		clause = clauses[indx]
		prev_clause = complete_instruction[indx-1]
		prev_nesting_level = prev_clause["nesting_level"]
		nesting_level = randint(0, 1) if prev_nesting_level == 0 else randint(0, 2)
		n_type = numbering_types[nesting_level]

		if prev_nesting_level == nesting_level:
			numbering[nesting_level] += 1
			index = numbering[nesting_level]
		elif prev_nesting_level < nesting_level:
			numbering[nesting_level] = 1
			index = numbering[nesting_level]
		elif prev_nesting_level > nesting_level:
			numbering[nesting_level] += 1
			index = numbering[nesting_level]

		complete_instruction.append({"clause": clause,
									 "index": index,
									 "nesting_level": nesting_level,
									 "numbering_type": n_type})

	for indx in range(len(clauses)):
		index = complete_instruction[indx]["index"]
		nesting_level = complete_instruction[indx]["nesting_level"]
		n_type = complete_instruction[indx]["numbering_type"]
		if n_type[0] == "arabic":
			clauses[indx] = '\t'*nesting_level + str(index) + n_type[1] + clauses[indx]

		elif n_type[0] == "roman":
			clauses[indx] = '\t'*nesting_level + str(to_roman(index)) + n_type[1] + clauses[indx]

		elif n_type[0] == "bullet":
			clauses[indx] = '\t'*nesting_level + n_type[1] + clauses[indx]

		elif n_type[0] == "latin":
			clauses[indx] = '\t'*nesting_level + consts.latin_alphabet[index-1] + n_type[1] + clauses[indx]

	instruction = "".join(clauses)

	# return instruction
	return clauses

def check_abiword():
	try:
		sb.call(["abiword", "--help"], stdout=sb.DEVNULL, stderr=sb.DEVNULL)
	except FileNotFoundError:
		logger.critical("abiword is not installed in the system.")
		raise SystemError("abiword is not installed in your system. "
			"If you use apt package manager try \"sudo apt install abiword\".")

	return 0

def check_os():
	global pltform
	pltform = platform 

	if platform == "linux" or platform == "linux2":
		if check_abiword() == 0:
			return platform

def parse_formats(fmts):
	if ('j' in fmts) and ('p' not in fmts):
		logger.error(f"Invalid formats: {fmts}. You can't use 'j' without 'p'.")
		raise ArgumentTypeError("Invalid value")

	if ('p' in fmts) and ('d' not in fmts):
		logger.error(f"Invalid formats: {fmts}. You can't use 'p' without 'd'.")
		raise ArgumentTypeError("Invalid value")

	if ('p' in fmts):
		check_os()

	return fmts

def mm_to_px(mm, dpi=300):
	return int((mm * (dpi/25.4)))

def PDFunits_to_px(units, dpi=300):
	inch = units / 72
	mm = inch * 25.4
	return mm_to_px(mm, dpi)

#Пересчет координат в форме [x1,y1,w,h]
def calculate_logo_coords():
	x0 = int(mm_to_px(consts.logo_w.mm))
	y0 = int(mm_to_px(consts.logo_h.mm))
	
	logo_coords = []
	logo_coords.append(int(mm_to_px(consts.left_margin.mm)) - consts.logo_offset)
	logo_coords.append(int(mm_to_px(consts.top_margin.mm)) - consts.logo_offset)
	logo_coords.append(x0)
	logo_coords.append(y0)

	return logo_coords, x0 * y0

def calculate_sign_coords(tmx, tmy, new_page=False):
	sign_coords = []

	if not new_page:
		x0 = mm_to_px(consts.sign_w.mm)
		y0 = mm_to_px(consts.sign_h.mm)

		x2 = PDFunits_to_px(consts.page_w) - mm_to_px(consts.right_margin.mm)
		
		y1 = tmy + consts.PDFunits_offset[1]
		y1 = PDFunits_to_px(y1)

		x1 = x2 - x0
		y2 = y1 + y0

	else:
		x0 = mm_to_px(consts.sign_w.mm)
		y0 = mm_to_px(consts.sign_h.mm)

		x2 = PDFunits_to_px(consts.page_w) - mm_to_px(consts.right_margin.mm)
		
		y1 = mm_to_px(consts.top_margin.mm)

		x1 = x2 - x0
		y2 = y1 + y0
	
	pd = consts.sign_padding
	sign_coords.append(x1)
	sign_coords.append(y1)
	sign_coords.append(x0)
	sign_coords.append(y0)

	return sign_coords, x0 * y0

def calculate_seal_coords(sign_coords, new_page=False):

	if not new_page:
		x0 = mm_to_px(consts.seal_w.mm)
		y0 = mm_to_px(consts.seal_h.mm)

		x2 = PDFunits_to_px(consts.page_w) - mm_to_px(consts.right_margin.mm)

		y1 = sign_coords[1] + 4.1666666666*consts.seal_offset[1]

		x1 = x2 - x0
		y2 = y1 + y0

	else:
		x0 = mm_to_px(consts.seal_w.mm)
		y0 = mm_to_px(consts.seal_h.mm)

		x2 = PDFunits_to_px(consts.page_w) - mm_to_px(consts.right_margin.mm)
		y1 = mm_to_px(consts.top_margin.mm)

		x1 = x2 - x0
		y2 = y1 + y0

	pd = consts.seal_padding
	seal_coords = [x1, y1, x0, y0]

	return seal_coords, x0 * y0

# coords: list - список из пар координат (x, y)
# pdf_path: str - путь к pdf файлу
# data: tuple - кортеж данных для генерации
def calculate_borders(original_coords, creator_and_date=False, task=False):

	def calculate(coords):
		if len(coords) == 1:
			x1 = min(coords)
			y1 = coords[0][1]
			y2 = coords[0][1]
		
		elif len(coords) > 1:
			x1 = min(coords)
			y1 = 10000
			y2 = 0

			for pair in coords:
				if pair[1] < y1:
					y1 = pair[1]

				if pair[1] > y2:
					y2 = pair[1]

		else:
			return []

		x1 = PDFunits_to_px(x1[0])
		y1 = PDFunits_to_px(y1)
		y2 = PDFunits_to_px(y2)

		x_offset = consts.text_borders[0]
		y_offset = consts.text_borders[1]
		font_height = mm_to_px(consts.font_height)
		if task:
			x = x1 - x_offset/2
			y = y1 - y_offset/2
			w = 2550 - 2*x1 + mm_to_px(15)
			h = y2 - y1 + y_offset/2
			return [[x,y,w,h],w*h]
		elif  creator_and_date:
			x = x1
			y = y1 - font_height
			w = 2550 - x1 - mm_to_px(15)
			h = y2 - y1  + y_offset
			return [[x,y,w,h],w*h]
		else:
			x = x1 - x_offset/2
			y = y1 - font_height
			w = 2550 - 2*x1 + mm_to_px(15)
			h = y2 - y1  + y_offset
			return [[x,y,w,h],w*h]

	if original_coords == ["page_break"]:
		return original_coords
	elif "page_break" in original_coords:
		splitted_coords = []
		result = []
		for pair in original_coords:
			if pair != "page_break":
				splitted_coords.append(pair)
			else:
				result.append(calculate(splitted_coords))
				result.append("page_break") 
				splitted_coords = []
	else:
		return calculate(original_coords)

	return result


# pdf_path: str - путь к pdf файлу
# data: tuple - кортеж данных для генерации
def calculate_text_coords(pdf_path, data,page):
	header, header_coords = data[0], []
	name, name_coords = data[1], []
	intro, intro_coords = data[2], []
	instruction, instruction_coords = data[3], [[] * i for i in range(len(data[3]) + 1)]
	responsible, responsible_coords = data[4], []
	creator, creator_coords = data[5], []
	date, date_coords = data[6], []

	reader = PdfReader(pdf_path)

	raw_data = []
	def visitor_t(text, cm, tm, fontDict, fontSize):
		raw_data.append([text, tm[4], tm[5]]) # [text, x1, y1]

	page.extract_text(visitor_text=visitor_t) # Посимвольное извлечение координат текста

	for i in range(len(raw_data)):
		raw_data[i][1] = int(raw_data[i][1])
		raw_data[i][2] = int(raw_data[i][2])

	# Объединение символов с одинаковыми координатами в строки
	# text - список со строками
	# coords - список с соответствующими строкам координатами
	text, coords = [], []
	for i in range(len(raw_data)):
		if [raw_data[i][1], raw_data[i][2]] not in coords:
			coords.append([raw_data[i][1], raw_data[i][2]])
			text.append(raw_data[i][0])
		else:
			text[-1] += raw_data[i][0]

	if (len(text) != len(coords)):
		logger.error("[text] != [coords]")
		raise SystemExit

	formatted_markup = {}
	for i in range(len(text)):
		if text[i] == '':
			continue

		formatted_markup[text[i]] = coords[i]
		
	# Если ключ словаря (строка в документе) входит в секцию данных для генерации,
	# то добавить координаты строки в соответствующий список
	logger.debug(raw_data)
	logger.debug(coords)
	logger.debug(text)
	logger.debug(formatted_markup)
	
	for k in list(formatted_markup):

		if ((k.replace('\n', '') in header) and (not name_coords)):
			val = formatted_markup.pop(k)
			header_coords.append(val)

		if ((k.replace('\n', '') in name) and (not intro_coords)):
			try:
				val = formatted_markup.pop(k)
				name_coords.append(val)
			except KeyError:
				pass

		if (k[k.find("\n") + 1 : ].replace('\n', '') in intro and (not instruction_coords[0])):
			try:
				val = formatted_markup.pop(k)
				intro_coords.append(val)
			except KeyError:
				pass

		for i in range(len(instruction)):
			task = instruction[i]["task_text"]
			task1 = re.sub("[^А-Яа-я0-9]", "", task)
			k1 = re.sub("[^А-Яа-я0-9]", "", k[k.find("\n") + 1 : ])
			k1 = k1[1:]
			if (k1 != "" and k1 in task1 and (not instruction_coords[i + 1]) and not k in '.' + date):
				try:
					logger.debug(k)
					logger.debug(k1)
					logger.debug(task)
					logger.debug(task1)
					val = formatted_markup.pop(k)
					instruction_coords[i].append(val)
				except KeyError:
					pass
		if (k.replace('\n', '') in responsible or k[k.find("\n") + 1 : ] in responsible and k[k.find("\n") + 1 : ] != ''):
			try:
				val = formatted_markup.pop(k)
				responsible_coords.append(val)
			except KeyError:
				pass

		if (k[k.find("\n") + 1 : ] in creator and k[k.find("\n") + 1 : ] != ''):
			try:
				val = formatted_markup.pop(k)
				creator_coords.append(val)
			except KeyError:
				pass
		if (k.replace('\n', '') in '.' + date):
			try:
				val = formatted_markup.pop(k)
				date_coords.append(val)
			except KeyError:
				pass

	header_coords.append("page_break")
	name_coords.append("page_break")
	intro_coords.append("page_break")
	instruction_coords.append(["page_break"])
	responsible_coords.append("page_break")
	creator_coords.append("page_break")
	date_coords.append("page_break")

	logger.debug(header_coords)
	logger.debug(name_coords)
	logger.debug(intro_coords)
	logger.debug(instruction_coords)
	logger.debug(responsible_coords)
	logger.debug(creator_coords)
	logger.debug(date_coords)
	
	header_coords = calculate_borders(header_coords)
	
	name_coords = calculate_borders(name_coords)
	
	intro_coords = calculate_borders(intro_coords)
	
	task_coords = []
	for task in instruction_coords:
		task_coords.append(calculate_borders(task, task=True))

	responsible_coords = calculate_borders(responsible_coords)

	creator_coords = calculate_borders(creator_coords, creator_and_date=True)

	date_coords = calculate_borders(date_coords, creator_and_date=True)

	# try:
	# 	intro_coords[0][1] -= 55
	# except TypeError:
	# 	pass

	# for i in range(len(task_coords)):
	# 	try:
	# 		task_coords[i][0][1] -= 80
	# 	except TypeError:
	# 		continue

	result = [header_coords, name_coords, intro_coords, task_coords, responsible_coords,
		creator_coords, date_coords]

	return result

