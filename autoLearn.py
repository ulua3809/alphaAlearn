import json
import os
import threading
from time import sleep
from typing import Literal
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import uluautil as ulua

browserdataPath = "./autodata1"
logpath = "./log.txt"
chromedriverPath = "./chromedriver.exe"
browserExecPath = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"

isreverse = False
startLessonid = "5e3bd2ae772dec30e915dc9b"
endLessonid = "tnt2p538g9"


def initize():
	"""
	use relative path to script
	"""
	global logpath, browserdataPath, chromedriverPath
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	browserdataPath = os.path.abspath(browserdataPath)
	chromedriverPath = os.path.abspath(chromedriverPath)
	if os.path.exists(logpath):
		os.remove(logpath)
	if not os.path.exists(browserdataPath):
		os.mkdir(browserdataPath)

	# initize driver
	service = Service(executable_path=chromedriverPath)
	chopt = webdriver.ChromeOptions()
	chopt.binary_location = browserExecPath
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
	chopt.add_argument("--user-data-dir=" + browserdataPath)
	# 启动浏览器
	webdriverObj = webdriver.Chrome(chopt, service=service)
	return webdriverObj


def logtoFile(str1: str):
	file1 = open(logpath, mode='a+', encoding="utf-8")
	file1.writelines(str1)
	file1.write("\n")
	file1.close()


def main(browser: webdriver.Chrome):
	browser.get("https://sxgxy.alphacoding.cn/classroom")
	while True:
		log = browser.get_log('performance')
		for entry in log:
			logdict = json.loads(entry["message"])
			logobj = ulua.perfLog(logdict=logdict)
			matchlog(logobj, browser=browser)
		sleep(1)


DataType = Literal["PostData", "ResponseBody"]


def getData(requestId: str, browser: webdriver.Chrome, type: DataType) -> dict:
	if type == "PostData":
		return browser.execute_cdp_cmd('Network.getRequestPostData', {'requestId': requestId})
	elif type == "ResponseBody":
		return browser.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestId})
	else:
		return {}


def matchlog(logobj: ulua.perfLog, browser: webdriver.Chrome):
	global isreverse
	if logobj.getLogMethod() == "Network.responseReceived":
		if logobj.getLogType() == "XHR":
			# print("-" * 50, "\nurl:{}\nrequestId:{}".format(logobj.getUrl(), logobj.getReqId()))
			if "recordStudyTime" in logobj.getUrl():
				Stime = ulua.stuTime(getData(logobj.getReqId(), browser, type="PostData"))
				ulua.logPrint("时长上报成功，开始:{},时长:{},课程id:{},题目类型:{}".format(Stime.getStartTime(), ms2time(Stime.getDuration()),
				                                                          Stime.getlessonId(), Stime.getlessonType()))
			elif "detail" in logobj.getUrl():
				lessonobj = ulua.lesson(getData(logobj.getReqId(), browser, type="ResponseBody"))
				logtoFile(json.dumps(lessonobj.getresBody()))
				if lessonobj.getlessonId() == startLessonid:
					isreverse = False
				elif lessonobj.getlessonId() == endLessonid:
					isreverse = True
				ulua.logPrint("标题:{},类型:{},课程id:{},已学时长:{},需要时长:{}mins,完成状态{},reversemode:{}".format(
				    lessonobj.getlessontitle(), lessonobj.getlessontype(), lessonobj.getlessonId(),
				    ms2time(lessonobj.getLearneddur()), lessonobj.getReqduration(), lessonobj.isLearned(), isreverse))
				pushmisson(browser, lessonobj)
			elif "myCoursesNew" in logobj.getUrl():
				# print(logobj.logdict)
				courlist = ulua.TotalTime(getData(logobj.getReqId(), browser, type="ResponseBody")).courselist
				for courses in courlist:
					if "studyDuration" in courses:
						studur = ms2time(int(courses["studyDuration"]))
					else:
						studur = ms2time(0)
					print("课程名称：{}\n已学时长：{}\n结束时间：{}\n探索度：{}%".format(courses["courseName"], studur, courses["endAt"],
					                                                  courses["learningProgress"]))


def ms2time(msint: int) -> str:
	ms = msint % 1000
	sec = (msint // 1000) % 60
	min = (msint // (1000 * 60)) % 60
	hour = (msint // (1000 * 60 * 60))
	return "{:02d}:{:02d}:{:02d}.{:03d}".format(hour, min, sec, ms)


def pushmisson(browser: webdriver.Chrome, lessonobj: ulua.lesson):

	missonObj = lessonobj.getmissonObj(webdriverObj=browser, isreverse=isreverse)
	if missonObj.missonmatched():
		missonThread = threading.Thread(target=missonObj.learn, name="lessonId {}".format(missonObj.getlessonId()), daemon=True)
		missonThread.start()
	else:
		print("misson id{} out of date skip".format(missonObj.getlessonId()))


if __name__ == "__main__":
	main(initize())
