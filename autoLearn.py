import json
import os
import multiprocessing as mult
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from browsermobproxy import Client, Server
import uluautil as ulua

browserdataPath = "./autodata"
chromedriverPath = "./chromedriver.exe"
mobproxyPath = "./browsermob-proxy-2.1.4/bin/browsermob-proxy.bat"
logpath = "./log.txt"


def initize():
	"""
	use relative path to script
	"""
	# initize path
	global browserdataPath, chromedriverPath, mobproxyPath, logpath
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	browserdataPath = os.path.abspath(browserdataPath)
	chromedriverPath = os.path.abspath(chromedriverPath)
	mobproxyPath = os.path.abspath(mobproxyPath)
	logpath = os.path.abspath(logpath)

	if os.path.exists(logpath):
		os.remove(logpath)

	proxyserver = Server(mobproxyPath)
	proxyserver.start()
	proxy = proxyserver.create_proxy()
	# initize driver
	service = Service(executable_path=chromedriverPath)
	chopt = webdriver.ChromeOptions()
	chopt.binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
	#屏蔽webdrive检测
	chopt.add_argument("--allow-running-insecure-content")
	chopt.add_argument("--disable-web-security")
	chopt.add_argument("--proxy-server={0}".format(proxy.proxy))
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
	return (webdriverObj, proxy)


def logtoFile(str1: str):
	file1 = open(logpath, mode='a+', encoding="utf-8")
	file1.writelines(str1)
	file1.write("\n")
	file1.close()


def main(browser: webdriver.Chrome, proxy: Client):
	#屏蔽webdrive检测
	browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
	    "source":
	    """
	Object.defineProperty(navigator, 'webdriver', {
	get: () => undefined
	})
	"""
	})

	browser.get("https://sxgxy.alphacoding.cn/")

	proxy.new_har(options={'captureContent': True, 'captureHeaders': True})
	while True:
		log = proxy.har
		proxy.new_har(options={'captureContent': True, 'captureHeaders': True})
		for entry in log["log"]["entries"]:
			logobj = ulua.harObj(logdict=entry)
			matchlog(logobj, browser=browser)
		sleep(1)


def matchlog(logobj: ulua.harObj, browser: webdriver.Chrome):

	# print("-" * 50)
	# print("url:", logobj.getUrl())
	if "recordStudyTime" in logobj.getUrl():
		Stime = ulua.stuTime(logobj.getRequset())
		ulua.logPrint("时长上报成功，开始:{},时长:{},课程id:{},题目类型:{}".format(Stime.getStartTime(),
		                                                          ms2time(Stime.getDuration()),
		                                                          Stime.getlessonId(),
		                                                          Stime.getlessonType()))
	elif "detail" in logobj.getUrl():
		lessonobj = ulua.lesson(logobj.getResponse())
		logtoFile(json.dumps(lessonobj.getresBody()))
		print("标题:{},类型:{},课程id:{},已学时长:{},需要时长:{}mins,完成状态{}".format(
		    lessonobj.getlessontitle(), lessonobj.getlessontype(), lessonobj.getlessonId(),
		    ms2time(lessonobj.getLearneddur()), lessonobj.getReqduration(), lessonobj.isLearned()))
		pushmisson(browser, lessonobj)


def ms2time(msint: int) -> str:
	ms = msint % 1000
	sec = (msint // 1000) % 60
	min = (msint // (1000 * 60)) % 60
	return "{:02d}:{:02d}.{:03d}".format(min, sec, ms)


missonproc = mult.Process()


def pushmisson(browser: webdriver.Chrome, lessonobj: ulua.lesson):
	missonObj = lessonobj.getmissonObj(webdriverObj=browser)

	if missonObj.missonmatched():
		missonObj.learn()
	else:
		print("misson id{} out of date skip".format(missonObj.getlessonId()))

	# Todo:fix webdriver multproc

	# global missonproc
	# missonObj = lessonobj.getmissonObj(webdriverObj=browser)
	# if missonObj.missonmatched():
	# 	if missonproc.is_alive():
	# 		print("Process {} time out,terminating".format(missonproc.name))
	# 		missonproc.terminate()
	# 	missonproc = mult.Process(target=missonObj.learn,
	# 	                          name="lessonId {}".format(missonObj.getlessonId()),
	# 	                          args=(browser, ))
	# 	missonproc.start()
	# else:
	# 	print("misson id{} out of date skip".format(missonObj.getlessonId()))


if __name__ == "__main__":
	# initize()
	webdriverObj, proxy = initize()
	main(webdriverObj, proxy)
