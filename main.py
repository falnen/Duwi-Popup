import webhost
from  Sockethost import liveListener, APP_CLIENT_ID
import webbrowser
import Persistence
from threading import Thread
from PIL import Image
import pystray

image = Image.open("Shock by @duwiexe.png")

class main():
    def __init__(self):
        self.token = None
        self.listener_thread = None

    def twitchAuthorize(self):
        webhost.webviewElementEdit('twitch-auth','Waiting on Auth...','null')
        webbrowser.open(f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={APP_CLIENT_ID}&redirect_uri=localhost:3000&scope=")
        self.token = webhost.getFragment()
        self.connect()

    def startListener(self):
        Persistence.saveTokenToFile(self.token)
        self.listener_thread = Thread(group=None,target=listener.start,kwargs={"accesstoken":self.token},daemon=True)
        self.listener_thread.start()
        webhost.webviewElementEdit('twitch-auth','Connected!','null')

    def connect(self):
        if self.token:
            valid = webhost.validateToken(self.token)
            if valid:
                self.startListener()
            else:
                webhost.webviewElementEdit('twitch-auth','Reconnect to Twitch','connect_button')

        else:
            webhost.webviewElementEdit('twitch-auth','Failed to connect... try again?','connect_button')

if __name__ == "__main__":

    listener = liveListener()
    savedtoken = Persistence.loadTokenFromFile()
    app = main()

    def onLoaded():
        if savedtoken:
            app.token = savedtoken
            app.connect()
            print("connected with saved token")
        else:
            print("need token")
            webhost.webviewElementEdit('twitch-auth','Connect to twitch','connect_button')
            
    def onClose():
        Persistence.saveTokenToFile(listener.accesstoken)
        webhost.webviewElementEdit('infoText','Closing ... please wait!')
        if app.listener_thread is not None and app.listener_thread.is_alive():
            listener.stop()
            app.listener_thread.join()
        trayicon.stop()
        webhost.window.destroy()
    
    def trayClick():
        webhost.window.show()

    def iconify():
        webhost.window.hide()
        webhost.webviewElementEdit('infoText','This window will open when Duwi comes online.<br>Minimize it to the tray for now and wait!<br>You can close the app with the X, or from the tray icon.')
        webhost.webviewElementEdit('twitch-auth','Connected!','null')
        
    def linkToDuwi():
        webbrowser.open("https://www.twitch.tv/duwiexe")

    trayicon = pystray.Icon('Duwi popup',title='Duwi popup',icon=image,menu=pystray.Menu(pystray.MenuItem('open',trayClick,default=True,visible=False),pystray.MenuItem('Exit',onClose)))
    traythread = Thread(group=None,target=trayicon.run,daemon=True)
    traythread.start()
    webhost.window.expose(app.twitchAuthorize,onClose,iconify,linkToDuwi)
    webhost.window.events.loaded += onLoaded
    webhost.webview.start()