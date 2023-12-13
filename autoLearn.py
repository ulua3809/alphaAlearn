import json
import os
import threading
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import uluautil as ulua
from uluautil import browser


def initize():
	"""
	use relative path to script
	"""
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	ulua.browserdataPath = os.path.abspath(ulua.browserdataPath)
	chromedriverPath = os.path.abspath(ulua.chromedriverPath)
	if os.path.exists(ulua.logpath):
		os.remove(ulua.logpath)
	if not os.path.exists(ulua.browserdataPath):
		os.mkdir(ulua.browserdataPath)

	# initize driver
	service = Service(executable_path=chromedriverPath)
	chopt = webdriver.ChromeOptions()
	chopt.binary_location = ulua.browserExecPath
	#屏蔽webdrive检测
	chopt.add_argument("--disable-web-security")
	chopt.add_argument("--allow-running-insecure-content")
	# 退出不关闭浏览器
	chopt.add_experimental_option("detach", True)
	# 关闭webdriver log输出
	chopt.add_experimental_option('excludeSwitches', ['enable-logging'])
	# 开启性能日志
	chopt.add_experimental_option("perfLoggingPrefs", {'enableNetwork': True})
	chopt.set_capability("goog:loggingPrefs", {"performance": "ALL"})
	# 使用默认用户数据
	chopt.add_argument("--user-data-dir=" + ulua.browserdataPath)
	# 启动浏览器
	global browser
	ulua.browser = webdriver.Chrome(chopt, service=service)
	browser = ulua.browser


def main():
	assert browser is not None
	browser.get("https://sxgxy.alphacoding.cn/classroom")
	while True:
		log = browser.get_log('performance')
		for entry in log:
			logdict = json.loads(entry["message"])
			logobj = ulua.perfLog(logdict=logdict)
			matchlog(logobj)
		sleep(1)


def matchlog(logobj: ulua.perfLog):
	global isEnd
	if logobj.getLogMethod() == "Network.responseReceived":
		if logobj.getLogType() == "XHR":
			# print("-" * 50, "\nurl:{}\nrequestId:{}".format(logobj.getUrl(), logobj.getReqId()))
			pkgobj = pkgHandler(logobj)
			url = logobj.getUrl()
			if "recordStudyTime" in url:
				pkgobj.StudyTime()
			elif "detail" in url:
				pkgobj.lessondetail()
			elif "myCoursesNew" in logobj.getUrl():
				pkgobj.CoursesInfo()


def pushmisson(lessonobj: ulua.lesson):
	assert browser is not None
	missonObj = lessonobj.getmissonObj(webdriverObj=browser)
	if missonObj.missonmatched():
		missonThread = threading.Thread(target=missonObj.learn, name="lessonId {}".format(missonObj.getlessonId()), daemon=True)
		missonThread.start()
	else:
		print("misson id{} out of date skip".format(missonObj.getlessonId()))


class pkgHandler():

	def __init__(self, logobj: ulua.perfLog) -> None:
		self.logobj = logobj

	def StudyTime(self):
		Stime = ulua.stuTime(self.logobj)
		if Stime.error:
			ulua.logPrint("时长上报出错，已记录日志")
			return
		tample = "时长已上报，开始:{},时长:{},课程id:{},题目类型:{}"
		logstr = tample.format(Stime.getStartTime(),
		                       ulua.ms2time(Stime.getDuration())[3:], Stime.getlessonId(), Stime.getlessonType())
		ulua.logPrint(logstr)

	def lessondetail(self):
		lessonobj = ulua.lesson(ulua.getData(self.logobj.getReqId(), type="ResponseBody"))
		if lessonobj.error:
			ulua.logPrint("题目获取出错，已记录日志")
			return
		# logtoFile(json.dumps(lessonobj.getresBody()))
		if lessonobj.getlessonId() == ulua.endLessonid:
			ulua.isEnd = True
		else:
			ulua.isEnd = False
		tample = "标题:{},类型:{},课程id:{},已学时长:{},需要时长:{}mins,完成状态{}"
		logstr = tample.format(lessonobj.getlessontitle(), lessonobj.getlessontype(), lessonobj.getlessonId(),
		                       ulua.ms2time(lessonobj.getLearneddur()), lessonobj.getReqduration(), lessonobj.isLearned())
		ulua.logPrint(logstr)
		pushmisson(lessonobj)

	def CoursesInfo(self):
		courseobj = ulua.TotalTime(self.logobj)
		if courseobj.error:
			ulua.logPrint("学习记录获取出错，已记录日志")
			return
		courlist = courseobj.courselist
		for courses in courlist:
			if "studyDuration" in courses:
				studur = ulua.ms2time(int(courses["studyDuration"]))
			else:
				studur = ulua.ms2time(0)
			tample = "\n课程名称：{}\n已学时长：{}\n结束时间：{}\n探索度：{}%"
			logstr = tample.format(courses["courseName"], studur, courses["endAt"], courses["learningProgress"])
			ulua.logPrint(logstr)


if __name__ == "__main__":
	initize()
	main()
