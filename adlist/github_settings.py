# Copy this file to github_settings.py (don't check it into github)

# Go to https://github.com/settings/developers

# Add a New OAuth2 App 

# Using ngrok is hard because the url changes every time you start ngrok

# If you are running on localhost, here are some settings:

# Application name: ChuckList Local
# Homepage Url: http://localhost:8000
# Application Description: Whatever
# Authorization callback URL: http://127.0.0.1:8000/oauth/complete/github/


# Using PythonAnywhere here are some settings:

# Application name: ChuckList PythonAnywhere
# Homepage Url: https://drchuck.pythonanywhere.com
# Application Description: Whatever
# Authorization callback URL: https://drchuck.pythonanywhere.com/oauth/complete/github/

# Also on PythonAnywhere, go into the Web tab and enable "Force HTTPS"
# so you don't get a redirect URI mismatch.

# Then copy the client_key and secret to this file

#SOCIAL_AUTH_GITHUB_KEY = 'bebcbc74fc4224ff11da'
#SOCIAL_AUTH_GITHUB_SECRET = '8a6b248ad1c32262fd10758280fd49a14ff0ab23'

SOCIAL_AUTH_GITHUB_KEY ='7e5de7863b6f1282d67e'
SOCIAL_AUTH_GITHUB_SECRET = 'f2ea6817be87048691c2674b0e0820c5feb23e88'

# The code below dynamically switches between non-social login.html 
# and social_login.html when we notice that social login has been
# configured in settings.py (later in the course)
# Or just uncomment the path above when you enable social login

