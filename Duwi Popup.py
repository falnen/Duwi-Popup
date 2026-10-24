from Utility import webview, window, validateToken, getFragment, webviewElementEdit, resourcePath
from  Sockethost import liveListener, APP_CLIENT_ID
import webbrowser
import Persistence
from threading import Thread
from PIL import Image
import pystray

image = Image.open(resourcePath("Shock by @duwiexe.png"))

class main():
    def __init__(self):
        self.token = None
        self.listener_thread = None

    def twitchAuthorize(self):
        webviewElementEdit('twitch-auth','Waiting on Auth...','null')
        webbrowser.open(f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={APP_CLIENT_ID}&redirect_uri=localhost:3000&scope=")
        self.token = getFragment()
        self.connect()

    def connect(self):
        if self.token:
            valid = validateToken(self.token)
            if valid:
                self.startListener()
            else:
                webviewElementEdit('Log','Authentication invalid - Reconnect to Twitch.')
                webviewElementEdit('twitch-auth','Reconnect to Twitch','connect_button')
        else:
            webviewElementEdit('Log','Failed to connect... try again?')
            webviewElementEdit('twitch-auth','Connect to Twitch','connect_button')

    def startListener(self):
        Persistence.saveTokenToFile(self.token)
        if self.listener_thread is not None:
            listener.stop()
            self.listener_thread.join()
        self.listener_thread = Thread(group=None,target=listener.start,kwargs={"accesstoken":self.token},daemon=True)
        self.listener_thread.start()
        webviewElementEdit("Log", 'Connected!')
        webviewElementEdit('twitch-auth',"Check out Duwi's channel!",'joinDuwi')
        

if __name__ == "__main__":

    listener = liveListener()
    savedtoken = Persistence.loadTokenFromFile()
    app = main()

    def onLoaded():
        if savedtoken:
            app.token = savedtoken
            app.connect()
            webviewElementEdit("Log", "Connected with saved token.")
        else:
            webviewElementEdit("Log", "Need token.")
            webviewElementEdit('twitch-auth','Connect to Twitch','connect_button')
            
    def onClose():
        Persistence.saveTokenToFile(listener.accesstoken)
        webviewElementEdit('Log','Closing ... please wait!')
        if app.listener_thread is not None and app.listener_thread.is_alive():
            listener.stop()
            app.listener_thread.join()
        if traythread is not None and traythread.is_alive():
            trayicon.stop()
        window.destroy()
    
    def trayClick():
        window.show()

    def iconify():
        window.hide()

    def linkToGithub():
        webbrowser.open("https://github.com/falnen/Duwi-Popup/tree/main")

    def linkToDuwi():
        webbrowser.open("https://www.twitch.tv/duwiexe")

    def linkTo(Domain=None):
        match Domain:
            case "Bsky":
                webbrowser.open("https://bsky.app/profile/duwiexe.bsky.social")
            case "Twitter":
                webbrowser.open("https://twitter.com/Duwi_EXE")
            case "Youtube":
                webbrowser.open("https://youtube.com/@duwiexe")
            case "Throne":
                webbrowser.open("https://throne.com/duwiexe")
            case "Kofi":
                webbrowser.open("https://ko-fi.com/duwiexe")

    trayicon = pystray.Icon('Duwi popup',title='Duwi popup',icon=image,menu=pystray.Menu(pystray.MenuItem('open',trayClick,default=True,visible=False),pystray.MenuItem('Exit',onClose)))
    traythread = Thread(group=None,target=trayicon.run,daemon=True)
    traythread.start()
    window.expose(
        app.twitchAuthorize,
        app.connect,
        onClose,
        iconify,
        linkToDuwi,
        linkToGithub,
        linkTo,
        app.connect)
    window.events.loaded += onLoaded
    webview.start()