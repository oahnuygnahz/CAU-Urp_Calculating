# -*- coding:utf-8 -*-
import urllib2
import cookielib
import time
import re


class lesson:
	# __course_number1 = '0'
	# __course_number2 = '0'
	# __course_name = '0'
	# __course_englishname = '0'
	# __credit = '0'
	# __course_attribute = '0'
	# __course_grade = '0'

	def __init__(self, c1='0', c2='0', cn='0', ce='0', cr='0', ca='0', cg='0'):
		self.__course_number1 = c1
		self.__course_number2 = c2
		self.__course_name = cn
		self.__course_englishname = ce
		self.__credit = cr
		self.__course_attribute = ca
		self.__course_grade = cg

	def get_course_number1(self):
		return self.__course_number1

	def get_course_name(self):
		return self.__course_name

	def get_credit(self):
		return self.__credit

	def get_course_grade(self):
		return self.__course_grade

	def get_mul(self):
		return float(self.__course_grade) * float(self.__credit)

	def change_course_grade(self, grade):
		self.__course_grade = grade

	def change_course_name(self, name):
		self.__course_name = name

	def change_credit(self, credit):
		self.__credit = credit


def login_test(userid, password):
	url = 'http://urpjw.cau.edu.cn/loginAction.do?dlfs=mh&mh_zjh=%s&mh_mm=%s'

	URL = url % (userid, password)

	Request = urllib2.Request(URL)

	try:
		Response = urllib2.urlopen(Request, timeout=30)
	except urllib2.URLError, e:
		print time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
		print e.reason
		time.sleep(5)

	result = Response.read()

	find = result.find('mainFrame')

	return find


def grade_change(grade_before):
	try:
		float(grade_before)
	except (ValueError, TypeError):
		return 0
	if float(grade_before) in range(90, 100):
		grade = 4.0
		return grade
	if float(grade_before) in range(85, 90):
		grade = 3.7
		return grade
	if float(grade_before) in range(82, 85):
		grade = 3.3
		return grade
	if float(grade_before) in range(78, 82):
		grade = 3.0
		return grade
	if float(grade_before) in range(75, 78):
		grade = 2.7
		return grade
	if float(grade_before) in range(72, 75):
		grade = 2.3
		return grade
	if float(grade_before) in range(68, 72):
		grade = 2.0
		return grade
	if float(grade_before) in range(64, 68):
		grade = 1.7
		return grade
	if float(grade_before) in range(60, 64):
		grade = 1.3
		return grade
	# Change failed grade's GPA
	if float(grade_before) < 5:
		grade = float(grade_before) * 0.6
		return grade
	return 0


def urp_login(userid, password):
	# Module1: Get userid and password. Output url_login.
	url_login = 'http://urpjw.cau.edu.cn/' \
	            'loginAction.do?dlfs=mh&mh_zjh=%s&mh_mm=%s' % (userid, password)

	# Module2: Get cookie though url_login.
	cookie = cookielib.MozillaCookieJar('cookie.txt')
	cookie_handler = urllib2.HTTPCookieProcessor(cookie)
	opener = urllib2.build_opener(cookie_handler)

	opener.open(url_login)

	# Module3: Use cookie to get gpa_text.
	info_url_name = 'http://urpjw.cau.edu.cn/gradeLnAllAction.do?type=ln&oper=qbinfo&lnxndm=2015-2016%D1%A7%C4%EA%C7%EF(%C8%FD%D1%A7%C6%DA)'
	request = urllib2.Request(info_url_name)
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	response = opener.open(request)

	gpa_text = response.read().decode('GBK')

	pattern = r'<td align="center">(.+?)</td>'

	match = re.findall(pattern, gpa_text, re.S)
	# Module4: Create a list to save lesson class , and save the info in it.
	lesson_list = []

	for i in range(6, len(match), 7):
		pattern = r'<p align="center">(.+?)&nbsp;</P>'
		grade = re.findall(pattern, match[i])

		match[i] = grade[0]
	# Save the info in it.
	for i in range(len(match) / 7):
		lesson_list.append('%s' % i)
		try:
			lesson_list[i] = lesson(match[i * 7], match[i * 7 + 1], match[i * 7 + 2], match[i * 7 + 3],
			                        match[i * 7 + 4], match[i * 7 + 5], match[i * 7 + 6])
		except IndexError:
			pass
	# Handle the course_name , make it easier to identify
	for i in range(len(lesson_list)):
		lesson_list[i].change_course_name(lesson_list[i].get_course_name().strip())

	# Module5: read Guiding teaching plan ,and get real grade
	info_url_name = 'http://urpjw.cau.edu.cn/gradeLnAllAction.do?type=ln&oper=lnFajhKcCjInfo&lnxndm=2015-2016%D1%A7%C4%EA%C7%EF(%C8%FD%D1%A7%C6%DA)'
	request = urllib2.Request(info_url_name)
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	response = opener.open(request)

	gpa_realtext = response.read().decode('GBK')

	pattern = '<td align="center">&nbsp;(.+?)</td>'

	gpa_real = re.findall(pattern, gpa_realtext, re.S)

	for i in range(0, len(gpa_real), 3):
		for j in range(len(lesson_list)):
			if lesson_list[j].get_course_name() == gpa_real[i].strip():
				lesson_list[j].change_course_grade(gpa_real[i + 2].strip())
	# Module6: To correct the results of the failed grade.
	info_url_name = 'http://urpjw.cau.edu.cn/gradeLnAllAction.do?type=ln&oper=bjg'
	request = urllib2.Request(info_url_name)
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	response = opener.open(request)

	gpa_failed_text = response.read().decode('GBK')

	pattern = r'<td align="center">(.+?)</td>'

	gpa_failed = re.findall(pattern, gpa_failed_text, re.S)

	for i in range(len(gpa_failed)):
		for j in range(len(lesson_list)):
			if lesson_list[j].get_course_name() == gpa_failed[i].strip():
				lesson_list[j].change_course_grade(grade_change(lesson_list[j].get_course_grade()))

	# Module7: Distinguish between the grades of each term.
	temp_term = re.findall(r'<a name="(.+?)" /></a>', gpa_text)

	flag = []
	term_list = []

	for i in range(len(temp_term)):
		flag.append(gpa_text.find(temp_term[i]))

	for i in range(0, len(flag), 1):
		if i == (len(flag) - 1):
			gpa_text_temp = gpa_text[flag[i]:]
		else:
			gpa_text_temp = gpa_text[flag[i]:flag[i + 1]]

		pattern = r'<td align="center">(.+?)</td>'

		grade_temp = re.findall(pattern, gpa_text_temp, re.S)

		term_list.append(len(grade_temp) / 7)
	# Module8: Delete double major grade and CET grade
	for i in range(len(lesson_list)):
		if lesson_list[i].get_course_name().find('（双学位）'.decode('utf-8')) > 1:
			lesson_list[i].change_credit(0)
		if lesson_list[i].get_course_name().find('CET'.decode('utf-8')) > 1:
			lesson_list[i].change_credit(0)

	# Module9: Calculate GPA.
	term_list_temp = [0]
	temp = 0
	for i in range(len(term_list)):
		temp = int(term_list[i]) + temp
		term_list_temp.append(temp)

	term_list = term_list_temp
	###
	x = float(0)
	y = float(0)
	for i in range(len(term_list) - 1):
		a = term_list[i]
		b = term_list[i + 1]
		for j in range(len(lesson_list[a:b])):
			lesson_list[a + j].change_course_grade(grade_change(lesson_list[a + j].get_course_grade()))
			x = x + lesson_list[a + j].get_mul()
			y = y + float(lesson_list[a + j].get_credit())
		try:
			print str(temp_term[i].encode('gbk')) + ': ' + '%.2f' % (x / y) + ' (real:%.4f)' % (x / y)
		except ZeroDivisionError:
			print '查询错误,您的成绩可能不存在!'.decode('utf-8').encode('gbk')
		x = float(0)
		y = float(0)


def userinfo_get(list_temp):
	print '欢迎使用 <中国农业大学URP平均绩点查询系统-ver1.3> Author: ZhangYunHao '.decode('utf-8').encode('gbk')
	print '报告BUG,请联系:QQ 3358023393(新号)'.decode('utf-8').encode('gbk')
	userid = raw_input('请输入您的学号(回车键结束):'.decode('utf-8').encode('gbk'))
	password = raw_input('请输入您的urp密码(回车键结束):'.decode('utf-8').encode('gbk'))
	if login_test(userid, password) < 1:
		print '您输入的 学号 或 密码 出现错误.请重新输入!'.decode('utf-8').encode('gbk')
		print ' '
		userinfo_get(list_temp)
		return 0
	list_temp[0] = userid
	list_temp[1] = password


userid = ''
password = ''
list_temp = [userid, password]
userinfo_get(list_temp)

print '登录成功!正在查询中......'.decode('utf-8').encode('gbk')
urp_login(list_temp[0], list_temp[1])

print '查询完毕!感谢您的使用! 作者:ZhangYunHao'.decode('utf-8').encode('gbk')
print '提示:此结果依据Urp系统成绩,可能和教务处成绩有出入(教务处可能存在特殊加权平均分)!'.decode('utf-8').encode('gbk')
end = raw_input('回车键关闭窗口!'.decode('utf-8').encode('gbk'))
