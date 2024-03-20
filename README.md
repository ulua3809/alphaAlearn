# alphacodeAlearn

# this repo is not maintained anymore !


## alpha coding Autolearning script powered by python

# support states

| mission Type           | states |
| :--------------------- | :----: |
| video                  |   ✔    |
| document               |   ✔    |
| single-choice          |   ✔    |
| multiple-choice        | ✔[^1]  |
| judgment               |   ✔    |
| short-answer           |   ✔    |
| code-fill              |   ✔    |
| programming            |   ✔    |
| programming-multi-File |   ✔    |
| match                  | ❌[^2]  |

[^1]:temporary not support finished question

[^2]: unsupport automatic complete but log the answer is support

# setup

```shell
pip install -r ./requirements.txt
python autoLearn.py
#login and select the lesson
#enjoy
```

# configure

```python
# your browser data path, relative to the script
browserdataPath = "./autodata"
# your log data path, relative to the script
logpath = "./log.txt"
# your chromedriver path, relative to the script
chromedriverPath = "./chromedriver.exe"
# your browser path, absolut path
browserExecPath ="C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
```

# Todo list

- [ ] improve the finish condition of multiple-choice 
- [ ] add finish detection
- [ ] implement match automatic
