import json
import time
from selenium import webdriver


class harObj:
	_logdict = {}

	def __init__(self, logdict: dict) -> None:
		self._logdict = logdict

	def getUrl(self) -> str:
		return self._logdict["request"]["url"]

	def getRequset(self) -> dict:
		return self._logdict["request"]

	def getResponse(self) -> dict:
		return self._logdict["response"]

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
			self._resbody = json.loads(questDict["content"]["text"])
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
			elif self._resbody["data"]["lesson"]["elements"][0][
			    "exerciseType"] == "multiple-choice":
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
			return video(self._resbody, webdriverObj=webdriverObj)
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

	def isLearned(self) -> bool:
		return lesson(resbody=self._resbody).isLearned()

	def missonmatched(self) -> bool:
		if self._webdriverObj:
			if self.getlessonId() in self._webdriverObj.current_url:
				return True
		return False

	def nextmisson(self):
		if self._webdriverObj:
			if self.missonmatched():
				nextBtn = self._webdriverObj.find_element(
				    by="xpath", value="/html/body/div[1]/div/div/div[1]/div[2]/div/button[3]")
				nextBtn.click()

	def learn(self):
		if self.isLearned() and False:
			print("arlready learned skip")
			self.nextmisson()
		print("unsupport type skip it")
		self.nextmisson()


class video(misson):

	def learn(self):
		if self.missonmatched():
			if self.isLearned() and False:
				print("arlready learned skip")
				self.nextmisson()
				return None
			learnedDur = (self.getLearneddur() // (1000 * 60)) % 60
			duration = self.getReqduration() - learnedDur + 1
			logPrint("正在看视频/文档：{},时长{}mins".format(self.getlessontitle(), duration))
			time.sleep(duration * 60)
			self.nextmisson()
