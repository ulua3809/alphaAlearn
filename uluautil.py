import json
import time
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class perfLog:
	logdict = {}

	def __init__(self, logdict: dict) -> None:
		self.logdict = logdict

	def getLogMethod(self) -> str:
		return self.logdict["message"]["method"]

	def getLogType(self) -> str:
		return self.logdict["message"]["params"]["type"]

	def getUrl(self) -> str:
		return self.logdict["message"]["params"]["response"]["url"]

	def getReqId(self) -> str:
		return self.logdict["message"]["params"]["requestId"]


class stuTime:
	stimeDic = {}
	postData = {}

	def __init__(self, studict: dict) -> None:
		self.stimeDic = studict
		self.postData = json.loads(studict["postData"])

	def getStartTime(self):
		timestamp = float(self.postData["beginAt"]) // 1000
		timeArr = time.localtime(timestamp)
		return time.strftime("%Y-%m-%d %H:%M:%S", timeArr)

	def getDuration(self) -> int:
		"""
		:Returns: millisecond of lenarned time"""
		return self.postData["duration"]

	def getlessonId(self):
		return self.postData["lessonId"]

	def getlessonType(self):
		return self.postData["type"]


class TotalTime:
	ttimeDic = {}
	resbody = {}
	courselist = []

	def __init__(self, studict: dict) -> None:
		self.stimeDic = studict
		self.resbody = json.loads(studict["body"])
		self.courselist = self.resbody["data"]["courses"]


class lesson:
	questDict = {}
	resbody = {}

	def __init__(self, questDict: dict = {}, resbody: dict = {}) -> None:
		if questDict:
			self.questDict = questDict
			self.resbody = json.loads(questDict["body"])
		if resbody:
			self.resbody = resbody

	def getresBody(self) -> dict:
		return self.resbody

	def getlessontitle(self) -> str:
		return self.resbody["data"]["lesson"]["title"]

	def getlessontype(self) -> str:
		# 视频
		if self.resbody["data"]["lesson"]["type"] == "video":
			return "video"
		# 文档
		elif self.resbody["data"]["lesson"]["type"] == "document":
			return "document"
		# 练习
		elif self.resbody["data"]["lesson"]["type"] == "single":
			# 单选题
			if self.resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "single-choice":
				return "single-choice"
			# 多选题
			elif self.resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "multiple-choice":
				return "multiple-choice"
			# 判断题
			elif self.resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "judgment":
				return "judgment"
			# 匹配题
			elif self.resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "match":
				return "match"
			# 简答题
			elif self.resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "short-answer":
				return "short-answer"
			# 程序填空
			elif self.resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "code-fill":
				return "code-fill"
			# 编程题
			elif self.resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "programming":
				return "programming"
			else:
				return "unkowntype,tittle:{}".format(self.getlessontitle())
		else:
			return "unkowntype,tittle:{}".format(self.getlessontitle())

	def getlessonId(self) -> str:
		return self.resbody["data"]["lesson"]["lessonId"]

	def getReqduration(self) -> int:
		"""
		get require learning duration
		:return: require minutes
		"""
		return self.resbody["data"]["lesson"]["minutes"]

	def getLearneddur(self) -> int:
		"""
		:Return: millisecond of Learned time """
		return self.resbody["data"]["learnData"]["duration"]

	def isLearned(self) -> bool:
		return False
		return self.resbody["data"]["learnData"]["aced"]

	def getmissonObj(self, webdriverObj: webdriver.Chrome):
		# if True:
		# 	return videoAndDoc(self.resbody, webdriverObj=webdriverObj)
		if self.getlessontype() in ["video", "document"]:
			return videoAndDoc(self.resbody, isreverse, webdriverObj=webdriverObj)
		elif self.getlessontype() in ["single-choice", "multiple-choice", "judgment"]:
			return Choice(self.resbody, isreverse, webdriverObj=webdriverObj)
		elif self.getlessontype() == "code-fill":
			return codeFill(self.resbody, isreverse, webdriverObj=webdriverObj)
		elif self.getlessontype() == "programming":
			return programming(self.resbody, isreverse, webdriverObj=webdriverObj)
		elif self.getlessontype() == "short-answer":
			return shortAnswer(self.resbody, isreverse, webdriverObj=webdriverObj)
		elif self.getlessontype() == "match":
			return match(self.resbody, isreverse, webdriverObj=webdriverObj)
		else:
			return misson(self.resbody, isreverse, webdriverObj=webdriverObj)


def logPrint(*Text: str):
	Time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	print(Time, end=" ")
	for log in Text:
		print(log, end=" ")
	print("\n", end="")


class misson():
	resbody = {}
	nextBtnXpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/button[3]'
	pervBtnXpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/button[1]'

	def __init__(self, resbody, isreverse, webdriverObj: webdriver.Chrome) -> None:
		self.resbody = resbody
		self.webdriverObj = webdriverObj
		self.isreverse = isreverse

	def jsclick(self, elements):
		self.webdriverObj.execute_script("arguments[0].click();", elements)

	def getLearneddur(self):
		return lesson(resbody=self.resbody).getLearneddur()

	def getlessonId(self) -> str:
		return lesson(resbody=self.resbody).getlessonId()

	def getlessontitle(self):
		return lesson(resbody=self.resbody).getlessontitle()

	def getReqduration(self):
		return lesson(resbody=self.resbody).getReqduration()

	def getresourceId(self) -> str:
		return self.resbody["data"]["lesson"]["elements"][0]["resourceId"]

	def isLearned(self) -> bool:
		# return False
		return lesson(resbody=self.resbody).isLearned()

	def missonmatched(self) -> bool:
		if self.getlessonId() in self.webdriverObj.current_url:
			return True
		return False

	def nextmisson(self):
		time.sleep(1)
		if not self.missonmatched():
			return None
		if not self.isreverse:
			nextBtn = self.webdriverObj.find_element(by=By.XPATH, value="{}".format(self.nextBtnXpath))
		else:
			nextBtn = self.webdriverObj.find_element(by=By.XPATH, value="{}".format(self.pervBtnXpath))
		self.jsclick(nextBtn)

	def learn(self):
		if not self.missonmatched():
			return None
		if self.isLearned():
			print("already Learned skip")
			self.nextmisson()
		else:
			print("unsupport type skip it")
			self.nextmisson()


class videoAndDoc(misson):

	def learn(self):
		if not self.missonmatched():
			return None
		if self.isLearned():
			print("arlready learned skip")
			self.nextmisson()
			return None

		learnedDur = (self.getLearneddur() // (1000 * 60)) % 60
		if self.getReqduration() > learnedDur:
			duration = self.getReqduration() - learnedDur + 1
		else:
			duration = self.getReqduration() + 1
		logPrint("正在看视频/文档：{},时长{}mins".format(self.getlessontitle(), duration))
		time.sleep(duration * 60)
		self.nextmisson()


class Choice(misson):
	commitBtnClass = "font-medium whitespace-nowrap shadow-sm rounded border focus:ring-2 focus:outline-none border-transparent text-white bg-success-600 hover:bg-success-700 focus:ring-primary-500 focus:ring-offset-1 px-4 py-2 text-base inline-flex items-center justify-center"
	__optBoxclass = "text-xl leading-12"

	def commit(self):
		if not self.missonmatched():
			return None
		comitBtn = self.webdriverObj.find_element(By.CSS_SELECTOR, "[class='{}']".format(self.commitBtnClass))
		self.jsclick(comitBtn)

	def learn(self):
		if not self.missonmatched():
			return None
		if self.isLearned():
			print("arlready learned skip")
			self.nextmisson()
			return None

		answerid = []
		for opt in self.resbody["data"]["lesson"]["exercises"][self.getresourceId()]["options"]:
			if "isCorrect" in opt and opt["isCorrect"]:
				answerid.append(opt["id"])
				print("正确选项：", opt["option"])
		time.sleep(0.5)
		if not self.missonmatched():
			return None
		anserList = self.webdriverObj.find_elements(By.XPATH, '//*[@class="{}"]'.format(self.__optBoxclass))
		for opt in anserList:
			if opt.get_attribute("value") in answerid:
				self.jsclick(opt)
		self.commit()
		self.nextmisson()


class codeFill(misson):
	comitBtnClass = "font-medium whitespace-nowrap shadow-sm rounded border focus:ring-2 focus:outline-none border-transparent text-white bg-success-600 hover:bg-success-700 focus:ring-primary-500 focus:ring-offset-1 px-4 py-2 text-sm inline-flex items-center justify-center"
	nextBtnClass = "font-medium whitespace-nowrap  rounded border focus:ring-2 focus:outline-none  text-blue-700 border-transparent bg-blue-100 hover:bg-blue-200 focus:ring-primary-500  focus:ring-offset-1 px-4 py-2 text-sm inline-flex items-center justify-center"
	waittime = 5

	def commit(self):
		if not self.missonmatched():
			return None
		comitBtn = self.webdriverObj.find_element(By.CSS_SELECTOR, "[class='{}']".format(self.comitBtnClass))
		self.jsclick(comitBtn)
		time.sleep(self.waittime)
		if not self.missonmatched():
			return None
		nextBtn = self.webdriverObj.find_element(By.CSS_SELECTOR, "[class='{}']".format(self.nextBtnClass))
		self.jsclick(nextBtn)

	def learn(self):
		if not self.missonmatched():
			return None
		if self.isLearned():
			print("arlready learned skip")
			self.nextmisson()
			return None

		fillDict = {}
		for ans in self.resbody["data"]["lesson"]["exercises"][self.getresourceId()]["fillBlanks"]:
			fillDict[ans["id"]] = ans["replaceCharacter"]
		for blkid in fillDict:
			print("blank id {},fill {}".format(blkid, fillDict[blkid]))
			textBox = self.webdriverObj.find_element(By.XPATH, '//*[@id="{}"]/div/input'.format(blkid))
			textBox.clear()
			textBox.send_keys(fillDict[blkid])
		time.sleep(0.5)
		self.commit()


class programming(codeFill):
	comitBtnClass = "font-medium whitespace-nowrap shadow-sm rounded border focus:ring-2 focus:outline-none border-transparent text-white bg-primary-600 hover:bg-primary-700 focus:ring-primary-500 focus:ring-offset-1 px-4 py-2 text-sm inline-flex items-center justify-center el-tooltip__trigger"
	nextBtnClass = "font-medium whitespace-nowrap  rounded border focus:ring-2 focus:outline-none  text-blue-700 border-transparent bg-blue-100 hover:bg-blue-200 focus:ring-primary-500  focus:ring-offset-1 px-4 py-2 text-sm inline-flex items-center justify-center"
	waittime = 15
	__ismultFile = False
	__singleAns = ""
	__AnsDict = {}

	def analyze(self):
		self.__AnsDict = {}
		if self.resbody["data"]["lesson"]["exercises"][self.getresourceId()]["codeSolutions"]:
			# 是多文件
			self.__ismultFile = True
			anslist: list = self.resbody["data"]["lesson"]["exercises"][self.getresourceId()]["codeSolutions"]
			persetlist: list = self.resbody["data"]["lesson"]["exercises"][self.getresourceId()]["precommonCode"]
			showLists = []
			for pset in persetlist:
				# 排除隐藏文件
				if not pset["hide"]:
					showLists.append(pset["fileName"])
			for ans in anslist:
				if ans["fileName"] in showLists:
					self.__AnsDict[ans["fileName"]] = ans["code"]
		else:
			self.__ismultFile = False
			self.__singleAns = self.resbody["data"]["lesson"]["exercises"][self.getresourceId()]["codeSolution"]

	def switchTab(self, tabname: str):
		fileTabTemplate = '//*[@class="el-tabs__nav-scroll"]//*[text()="{}"]'
		if not self.missonmatched():
			return None
		tabbtn = self.webdriverObj.find_element(By.XPATH, fileTabTemplate.format(tabname))
		print("switch to {}".format(tabname))
		self.jsclick(tabbtn)

	def fillcode(self, answer: str):
		codeBoxclass = ".CodeMirror-lines"
		# 跳过空代码，多为测试类
		if answer == "":
			return None
		if not self.missonmatched():
			return None
		# 通过点击获取元素
		self.webdriverObj.find_element(By.CSS_SELECTOR, codeBoxclass).click()
		codeBox = self.webdriverObj.switch_to.active_element
		codeBox.send_keys(Keys.CONTROL, "a")
		codeBox.send_keys(Keys.BACKSPACE)
		pyperclip.copy(answer)
		codeBox.send_keys(Keys.CONTROL, "v")
		print("代码:")
		print("-" * 50)
		print(answer)
		print("-" * 50)

	def learn(self):
		if not self.missonmatched():
			return None
		if self.isLearned():
			print("arlready learned skip")
			self.nextmisson()
			return None
		self.analyze()
		if self.__ismultFile == False:
			self.fillcode(self.__singleAns)
		else:
			for filename in self.__AnsDict:
				if self.missonmatched():
					self.switchTab(filename)
					print(filename)
					time.sleep(1)
					self.fillcode(self.__AnsDict[filename])
		self.commit()


class shortAnswer(Choice):

	def learn(self):
		if not self.missonmatched():
			return None
		if self.isLearned():
			print("arlready learned skip")
			self.nextmisson()
			return None

		textLocClass = "markdown-editor border flex overflow-hidden h-full"
		answer: str = self.resbody["data"]["lesson"]["exercises"][self.getresourceId()]["answers"]["answer"]
		time.sleep(2)
		if not self.missonmatched():
			return None
		self.webdriverObj.find_element(By.CSS_SELECTOR, "[class='{}']".format(textLocClass)).click()
		textBox = self.webdriverObj.switch_to.active_element
		textBox.send_keys(Keys.CONTROL, "a")
		textBox.send_keys(Keys.BACKSPACE)
		pyperclip.copy(answer)
		textBox.send_keys(Keys.CONTROL, "v")
		print("解答:" * 50)
		print("-" * 50)
		print(answer)
		print("-" * 50)
		time.sleep(1)
		self.commit()
		time.sleep(4)
		if not self.missonmatched():
			return None
		self.nextmisson()


class match(misson):

	def learn(self):
		if not self.missonmatched():
			return None
		if self.isLearned():
			print("arlready learned skip")
			self.nextmisson()
			return None

		print("unsupport type ,analize answer")
		for ans in self.resbody["data"]["lesson"]["exercises"][self.getresourceId()]["matchAnswers"]:
			title = ans["title"]
			items = []
			for obj in ans["items"]:
				items.append(obj["name"])
			print("-" * 50)
			print("组：{}".format(title))
			print("选项\n{}".format(items))
			print("-" * 50)
		time.sleep(300)
		self.nextmisson()
