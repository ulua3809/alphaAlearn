from fileinput import filename
import json
import time
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class perfLog:
	_logdict = {}

	def __init__(self, logdict: dict) -> None:
		self._logdict = logdict

	def getLogMethod(self) -> str:
		return self._logdict["message"]["method"]

	def getLogType(self) -> str:
		return self._logdict["message"]["params"]["type"]

	def getUrl(self) -> str:
		return self._logdict["message"]["params"]["response"]["url"]

	def getReqId(self) -> str:
		return self._logdict["message"]["params"]["requestId"]

	def getLogdict(self) -> dict:
		return self._logdict


class stuTime:
	_StimeDic = {}
	_postData = {}

	def __init__(self, studict: dict) -> None:
		self._StimeDic = studict
		self._postData = json.loads(studict["postData"])

	def getpostdata(self) -> dict:
		return self._postData

	def getStartTime(self):
		timestamp = float(self._postData["beginAt"]) // 1000
		timeArr = time.localtime(timestamp)
		return time.strftime("%Y-%m-%d %H:%M:%S", timeArr)

	def getDuration(self) -> int:
		"""
		:Returns: millisecond of lenarned time"""
		return self._postData["duration"]

	def getlessonId(self):
		return self._postData["lessonId"]

	def getlessonType(self):
		return self._postData["type"]


class lesson:
	_questDict = {}
	_resbody = {}

	def __init__(self, questDict: dict = {}, resbody: dict = {}) -> None:
		if questDict:
			self._questDict = questDict
			self._resbody = json.loads(questDict["body"])
		if resbody:
			self._resbody = resbody

	def getresBody(self) -> dict:
		return self._resbody

	def getlessontitle(self) -> str:
		return self._resbody["data"]["lesson"]["title"]

	def getlessontype(self) -> str:
		# 视频
		if self._resbody["data"]["lesson"]["type"] == "video":
			return "video"
		# 文档
		elif self._resbody["data"]["lesson"]["type"] == "document":
			return "document"
		# 练习
		elif self._resbody["data"]["lesson"]["type"] == "single":
			# 单选题
			if self._resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "single-choice":
				return "single-choice"
			# 多选题
			elif self._resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "multiple-choice":
				return "multiple-choice"
			# 判断题
			elif self._resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "judgment":
				return "judgment"
			# 匹配题
			elif self._resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "match":
				return "match"
			# 简答题
			elif self._resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "short-answer":
				return "short-answer"
			# 程序填空
			elif self._resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "code-fill":
				return "code-fill"
			# 编程题
			elif self._resbody["data"]["lesson"]["elements"][0]["exerciseType"] == "programming":
				return "programming"
			else:
				return "unkowntype,tittle:{}".format(self.getlessontitle())
		else:
			return "unkowntype,tittle:{}".format(self.getlessontitle())

	def getlessonId(self) -> str:
		return self._resbody["data"]["lesson"]["lessonId"]

	def getReqduration(self) -> int:
		"""
		get require learning duration
		:return: require minutes
		"""
		return self._resbody["data"]["lesson"]["minutes"]

	def getLearneddur(self) -> int:
		"""
		:Return: millisecond of Learned time """
		return self._resbody["data"]["learnData"]["duration"]

	def isLearned(self) -> bool:
		return self._resbody["data"]["learnData"]["aced"]

	def getmissonObj(self, webdriverObj: webdriver.Chrome):
		if self.getlessontype() in ["video", "document"]:
			return videoAndDoc(self._resbody, webdriverObj=webdriverObj)
		elif self.getlessontype() in ["single-choice", "multiple-choice", "judgment"]:
			return Choice(self._resbody, webdriverObj=webdriverObj)
		elif self.getlessontype() == "code-fill":
			return codeFill(self._resbody, webdriverObj=webdriverObj)
		elif self.getlessontype() == "programming":
			return programming(self._resbody, webdriverObj=webdriverObj)
		elif self.getlessontype() == "short-answer":
			return shortAnswer(self._resbody, webdriverObj=webdriverObj)
		elif self.getlessontype() == "match":
			return match(self._resbody, webdriverObj=webdriverObj)
		else:
			return misson(self._resbody, webdriverObj=webdriverObj)


def logPrint(*Text: str):
	Time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	print(Time, end=" ")
	for log in Text:
		print(log, end=" ")
	print("\n", end="")


class misson():
	_resbody = {}
	_webdriverObj = None

	def __init__(self, resbody, webdriverObj: webdriver.Chrome) -> None:
		self._resbody = resbody
		self._webdriverObj = webdriverObj

	def getLearneddur(self):
		return lesson(resbody=self._resbody).getLearneddur()

	def getlessonId(self) -> str:
		return lesson(resbody=self._resbody).getlessonId()

	def getlessontitle(self):
		return lesson(resbody=self._resbody).getlessontitle()

	def getReqduration(self):
		return lesson(resbody=self._resbody).getReqduration()

	def getresourceId(self) -> str:
		return self._resbody["data"]["lesson"]["elements"][0]["resourceId"]

	def isLearned(self) -> bool:
		return lesson(resbody=self._resbody).isLearned()

	def missonmatched(self) -> bool:
		if self._webdriverObj:
			if self.getlessonId() in self._webdriverObj.current_url:
				return True
		return False

	def nextmisson(self):
		if self.missonmatched():
			if self._webdriverObj:
				if self.missonmatched():
					nextBtn = self._webdriverObj.find_element(by="xpath",
					                                          value="/html/body/div[1]/div/div/div[1]/div[2]/div/button[3]")
					nextBtn.click()

	def learn(self):
		if self.missonmatched():
			if self.isLearned():
				print("arlready learned skip")
				self.nextmisson()
			print("unsupport type skip it")
			self.nextmisson()


class videoAndDoc(misson):

	def learn(self):
		if self.missonmatched():
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

	def commit(self):
		if self._webdriverObj:
			comitBtn = self._webdriverObj.find_element(
			    By.CSS_SELECTOR,
			    "[class='font-medium whitespace-nowrap shadow-sm rounded border focus:ring-2 focus:outline-none border-transparent text-white bg-success-600 hover:bg-success-700 focus:ring-primary-500 focus:ring-offset-1 px-4 py-2 text-base inline-flex items-center justify-center']"
			)
			comitBtn.click()

	def learn(self):
		if self.missonmatched():
			answerid = []
			for opt in self._resbody["data"]["lesson"]["exercises"][self.getresourceId()]["options"]:
				if opt["isCorrect"]:
					answerid.append(opt["id"])
					print("正确选项：", opt["option"])
			if self.isLearned():
				print("arlready learned skip")
				self.nextmisson()
				return None
			if self._webdriverObj:
				self._webdriverObj.implicitly_wait(2)
				anserList = self._webdriverObj.find_elements(By.CSS_SELECTOR, ".text-xl.leading-12")
				for opt in anserList:
					if opt.get_attribute("value") in answerid:
						opt.click()
				self.commit()
			time.sleep(5)
			self.nextmisson()


class codeFill(misson):
	_comitBtnClass = "font-medium whitespace-nowrap shadow-sm rounded border focus:ring-2 focus:outline-none border-transparent text-white bg-success-600 hover:bg-success-700 focus:ring-primary-500 focus:ring-offset-1 px-4 py-2 text-sm inline-flex items-center justify-center"
	_nextBtnClass = "font-medium whitespace-nowrap  rounded border focus:ring-2 focus:outline-none  text-blue-700 border-transparent bg-blue-100 hover:bg-blue-200 focus:ring-primary-500  focus:ring-offset-1 px-4 py-2 text-sm inline-flex items-center justify-center"
	_waittime = 5

	def commit(self):
		if self._webdriverObj:
			comitBtn = self._webdriverObj.find_element(By.CSS_SELECTOR, "[class='{}']".format(self._comitBtnClass))
			comitBtn.click()
			time.sleep(self._waittime)
			nextBtn = self._webdriverObj.find_element(By.CSS_SELECTOR, "[class='{}']".format(self._nextBtnClass))
			nextBtn.click()

	def learn(self):
		if self.missonmatched():
			fillDict = {}
			for ans in self._resbody["data"]["lesson"]["exercises"][self.getresourceId()]["fillBlanks"]:
				fillDict[ans["id"]] = ans["matchRule"]
				print("blank id {},fill {}".format(ans["id"], ans["matchRule"]))
			if self._webdriverObj:
				if self.isLearned():
					print("arlready learned skip")
					self.nextmisson()
					return None
				self._webdriverObj.implicitly_wait(2)
				for blkid in fillDict:
					textBox = self._webdriverObj.find_element(By.XPATH, '//*[@id="{}"]/div/input'.format(blkid))
					textBox.clear()
					textBox.send_keys(fillDict[blkid])
				time.sleep(2)
				if self.missonmatched():
					self.commit()


class programming(codeFill):
	_codeAns = ""
	_comitBtnClass = "font-medium whitespace-nowrap shadow-sm rounded border focus:ring-2 focus:outline-none border-transparent text-white bg-primary-600 hover:bg-primary-700 focus:ring-primary-500 focus:ring-offset-1 px-4 py-2 text-sm inline-flex items-center justify-center el-tooltip__trigger"
	_nextBtnClass = "font-medium whitespace-nowrap  rounded border focus:ring-2 focus:outline-none  text-blue-700 border-transparent bg-blue-100 hover:bg-blue-200 focus:ring-primary-500  focus:ring-offset-1 px-4 py-2 text-sm inline-flex items-center justify-center"
	_waittime = 15

	def ismultiFile(self):
		if self._resbody["data"]["lesson"]["exercises"][self.getresourceId()]["codeSolutions"]:
			anslist: list = self._resbody["data"]["lesson"]["exercises"][self.getresourceId()]["codeSolutions"]
			showLists = []
			cslist: list = self._resbody["data"]["lesson"]["exercises"][self.getresourceId()]["precommonCode"]
			for pset in cslist:
				if pset["hide"] == False:
					showLists.append(pset["fileName"])
			if len(showLists) == 1:
				for ans in anslist:
					if ans["fileName"] == showLists[0]:
						self._codeAns = ans["code"]
				return False
			else:
				return True
		return False

	def learn(self):
		if self.missonmatched():
			if self.isLearned():
				print("arlready learned skip")
				self.nextmisson()
				return None
			if self.ismultiFile():
				print("unsupport muilt file ,analize answer")
				for file in self._resbody["data"]["lesson"]["exercises"][self.getresourceId()]["codeSolutions"]:
					fileName = file["fileName"]
					answer = file["code"]
					print("-" * 50)
					print("文件名：{}".format(fileName))
					print("-" * 50)
					print(answer)
					print("-" * 50)
				time.sleep(300)
				if self.missonmatched():
					self.nextmisson()
			if self._codeAns == "":
				self._codeAns: str = self._resbody["data"]["lesson"]["exercises"][self.getresourceId()]["codeSolution"]
			if self._webdriverObj:
				self._webdriverObj.implicitly_wait(2)
				if self.missonmatched():
					textBox = self._webdriverObj.find_element(By.CSS_SELECTOR, ".CodeMirror-lines")
					textBox.click()
					textBox = self._webdriverObj.switch_to.active_element
					textBox.send_keys(Keys.CONTROL, "a")
					textBox.send_keys(Keys.BACKSPACE)
					pyperclip.copy(self._codeAns)
					textBox.send_keys(Keys.CONTROL, "v")
					print("-" * 50)
					print("解法\n{}".format(self._codeAns))
					print("-" * 50)
					time.sleep(3)
					if self.missonmatched():
						self.commit()


class shortAnswer(Choice):

	def learn(self):
		textLocClass = "markdown-editor border flex overflow-hidden h-full"
		answer: str = self._resbody["data"]["lesson"]["exercises"][self.getresourceId()]["answers"]["answer"]

		if self.missonmatched():
			if self.isLearned():
				print("arlready learned skip")
				self.nextmisson()
				return None
			if self._webdriverObj:
				self._webdriverObj.implicitly_wait(2)
				textBox = self._webdriverObj.find_element(By.CSS_SELECTOR, "[class='{}']".format(textLocClass))
				textBox.click()
				textBox = self._webdriverObj.switch_to.active_element
				textBox.send_keys(Keys.CONTROL, "a")
				textBox.send_keys(Keys.BACKSPACE)
				pyperclip.copy(answer)
				textBox.send_keys(Keys.CONTROL, "v")
				print("-" * 50)
				print("解法\n{}".format(answer))
				print("-" * 50)
				time.sleep(3)
				if self.missonmatched():
					self.commit()
					time.sleep(4)
					self.nextmisson()


class match(misson):

	def learn(self):
		if self.isLearned():
			print("arlready learned skip")
			self.nextmisson()
			return None
		print("unsupport type ,analize answer")
		for ans in self._resbody["data"]["lesson"]["exercises"][self.getresourceId()]["matchAnswers"]:
			title = ans["title"]
			items = []
			for obj in ans["items"]:
				items.append(obj["name"])
			print("-" * 50)
			print("组：{}".format(title))
			print("选项\n{}".format(items))
			print("-" * 50)
		time.sleep(300)
		if self.missonmatched():
			self.nextmisson()
