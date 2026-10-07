import httphost
from  Sockethost import liveListener, APP_CLIENT_ID
import webbrowser
import Persistence
from threading import Thread
from PIL import Image
import webview
import pystray

image = Image.open("Shock by @duwiexe.png")

class main():
    def __init__(self):
        self.token = None
        self.listener_thread = None

    def twitchAuthorize(self):
        window.evaluate_js(
            r'''
            document.getElementById("twitch-auth").textContent = "Waiting on Auth..."
            document.getElementById("twitch-auth").onclick = null
            ''')
        webbrowser.open(f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={APP_CLIENT_ID}&redirect_uri=http://localhost:3000&scope=")
        self.token = httphost.getFragment()
        self.connect()

    def startListener(self):
        Persistence.saveTokenToFile(self.token)
        self.listener_thread = Thread(group=None,target=listener.start,kwargs={"accesstoken":self.token},daemon=True)
        self.listener_thread.start()
        window.evaluate_js(
            r'''
            document.getElementById("twitch-auth").textContent = "Connected!"
            document.getElementById("twitch-auth").onclick = null
            ''')

    def connect(self):
        if self.token:
            valid = httphost.validateToken(self.token)
            if valid:
                self.startListener()
            else:
                window.evaluate_js(
                    r'''
                    document.getElementById("twitch-auth").textContent = "Reconnect to Twitch"
                    document.getElementById("twitch-auth").onclick = connect_button
                    ''')
        else:
            window.evaluate_js(
                r'''
                document.getElementById("twitch-auth").textContent = "Failed to connect... try again?"
                document.getElementById("twitch-auth").onclick = connect_button
                ''')

if __name__ == "__main__":

    window = webview.create_window('DUWI',url='interface.html',frameless=True, easy_drag=False, width=400, height=200, min_size=(400,200), resizable=False, transparent=True, on_top=True)
    listener = liveListener(window=window)
    savedtoken = Persistence.loadTokenFromFile()
    app = main()

    def onLoaded():

        if savedtoken:
            app.token = savedtoken
            app.connect()
            print("connected with saved token")
        else:
            print("need token")
            window.evaluate_js(
                r'''
                document.getElementById("twitch-auth").textContent = "Connect to twitch"
                document.getElementById("twitch-auth").onclick = connect_button
                ''')
            
    def onClose():
        Persistence.saveTokenToFile(listener.accesstoken)
        window.evaluate_js(
            r'''
            document.getElementById("infoText").textContent = "Closing ... please wait!"
            ''')
        if app.listener_thread is not None and app.listener_thread.is_alive():
            listener.stop()
            app.listener_thread.join()
        trayicon.stop()
        window.destroy()
    
    def trayClick():
        window.show()

    def iconify():
        window.hide()
        window.evaluate_js(
            r'''
            document.getElementById("infoText").innerHTML = "This window will open when Duwi comes online.<br>Minimize it to the tray for now and wait!<br>You can close the app with the X, or from the tray icon."
            document.getElementById("twitch-auth").textContent = "Connected!"
            document.getElementById("twitch-auth").onclick = null
            ''')
        
    def linkToDuwi():
        webbrowser.open("https://www.twitch.tv/duwiexe")

    trayicon = pystray.Icon('Duwi popup',title='Duwi popup',icon=image,menu=pystray.Menu(pystray.MenuItem('open',trayClick,default=True,visible=False),pystray.MenuItem('Exit',onClose)))
    traythread = Thread(group=None,target=trayicon.run,daemon=True)
    traythread.start()
    window.expose(app.twitchAuthorize,onClose,iconify,linkToDuwi)
    window.events.loaded += onLoaded
    webview.start()