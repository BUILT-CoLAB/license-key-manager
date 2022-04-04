# License Key Manager

[API Documentation](https://documenter.getpostman.com/view/20172540/UVsSP3vk)

# How to run

> Update: Due to some unexpected virtual environment distinctions between Win/Linux distributions (namely environment variables), the system will now run in a global scenario without the need for a Virtual Environment.

**Step 1:** From the main directory (the repository's directory), run the following command:

```
pip install -r requirements.txt
```

**Step 2:** Set up the env variable for flask. This process has two commands, which the one that fits your OS:

Windows:
```
set FLASK_APP=bin
$env:FLASK_APP = "bin"
```

Linux:
```
export FLASK_APP=bin
```

**Step 3:** Run the flask application using the following commands:

Windows / Linux:
```
python3 -m flask run
```

If you are in a Linux distribution, you can just type: ```flask run```

By default, the website will be available inside ```http://localhost:5000/```