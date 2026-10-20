from webhost import validateToken, webviewElementEdit, window
from websockets.sync.client import connect,ClientConnection
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from playsound3 import playsound
from json import loads
from threading import Timer,Lock
import requests

APP_TIMEOUT = 600  #INT between 10 and 600
APP_CLIENT_ID = "5wzg88m34ulgtxj4fdfazf9d2mpxq1"
WS_URL = f'wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds={APP_TIMEOUT}'
EVENT_SUB_URL = "https://api.twitch.tv/helix/eventsub/subscriptions"
API_URL = "https://api.twitch.tv/helix/channels"
DUWI_ID = '463761283'

class liveListener():
    def __init__(self):
        self.accesstoken = None
        self._current_websocket = None
        self._old_websocket: ClientConnection = None
        self._watchdog = None
        self._watchdog_lock = Lock()
        self._reconnect_limit = 0

    def _startWatchdog(self):
        with self._watchdog_lock:
            if self._watchdog is not None:
                self._watchdog.cancel()
            self._watchdog = Timer(APP_TIMEOUT, self._timeout,)
            self._watchdog.daemon = True
            self._watchdog.start()

    def _timeout(self):
        if self._current_websocket is not None:
            self._current_websocket.close()
        webviewElementEdit('Log', 'Timed out, Reconnecting...')
        self.start()

    def start(self,URL:str = WS_URL,accesstoken:str = None):
        if accesstoken:
            self.accesstoken = accesstoken
        try:
            with connect(URL) as ws:
                self._current_websocket = ws
                validationcycle = 0 #Token must be validated every hour.
                webviewElementEdit("Log", "Ready! Waiting on events...")
                while True:
                    validationcycle += 1
                    if validationcycle >= 6:
                        validationcycle = 0
                        if not validateToken(self.accesstoken):
                            self.stop()
                            window.show()
                            webviewElementEdit("Log","Authentication revoked or expired, Please re-authenticate.")
                            webviewElementEdit('twitch-auth','Connect to Twitch','connect_button')
                            break
                    message = loads(ws.recv())
                    self._reconnect_limit = 0
                    self._handleMessage(message)

        except Exception as e:
            print(f'Error - {type(e)} - {e.args}')
            self._reconnect_limit += 1
            if self._reconnect_limit >= 5:
                webviewElementEdit("Log", "Reconnect limit reached, Is there a network issue?")
                webviewElementEdit('twitch-auth','Retry connection','authBypassConnect')
                self.stop()
                window.show()
            elif isinstance(e, ConnectionClosedOK):
                pass
            elif isinstance(e, ConnectionClosedError):
                webviewElementEdit("Log", "Connection dropped, Reconnecting...")
                self.start()
            elif isinstance(e, OSError):
                webviewElementEdit("Log", rf"Network error - {e}")
                self.start()
            else:
                webviewElementEdit("Log", rf"Unknow error - {e}")
                webviewElementEdit('twitch-auth','Retry connection','authBypassConnect')
                window.show()
                self.stop()

    def stop(self):
        self._watchdog.cancel()
        self._watchdog.join()
        self._current_websocket.close()

    def _handleMessage(self,message:dict):
        self._startWatchdog()
        metadata = message["metadata"]
        payload = message["payload"]
        match metadata["message_type"]:
            case "session_welcome":
                if self._old_websocket is not None:
                    self._old_websocket.close()
                    self._old_websocket = None
                else:
                    self.sessionid = payload["session"]["id"]
                    self._requestSubscription(self.sessionid,self.accesstoken)
            case "notification":
                self._receiveNotification(metadata,payload)
            case "session_keepalive":
                #Sent every APP_TIMEOUT seconds if no notification is received
                pass
            case "session_reconnect":
                self._receiveReconnect(payload)
            case "revocation":
                self._receiveRevocation(metadata,payload)
            case _:
                webviewElementEdit("log", rf"Unknown message - {message}")
    
    def _requestSubscription(self,sessionid:str,accesstoken:str):
        header = {
            "Authorization": f"Bearer {accesstoken}",
            "Client-Id": APP_CLIENT_ID,
            "Content-Type": "application/json"
            }
        body = {
            "type": None,
            "version": "1",
            "condition": {
                "broadcaster_user_id": DUWI_ID
            },
            "transport": {
                "method": "websocket",
                "session_id": sessionid
            }
        }
        body["type"] = 'stream.online'
        sub1 = requests.post(EVENT_SUB_URL,headers=header,json=body)
        body["type"] = 'stream.offline'
        sub2 = requests.post(EVENT_SUB_URL,headers=header,json=body)
        if sub1.status_code !=202 or sub2.status_code !=202:
            webviewElementEdit("Log", rf"Failed to subscribe to events. (Sub1:{sub1.status_code},Sub2:{sub2.status_code})")
            self.stop()
            window.show()

    def _receiveNotification(self,metadata:dict,payload:dict):
        notification = payload["subscription"]["type"]
        match notification:
            case 'stream.online':
                channelrequest = requests.get(f"{API_URL}?broadcaster_id={DUWI_ID}",headers={"Authorization": f"Bearer {self.accesstoken}","Client-Id": APP_CLIENT_ID,"Content-Type": "application/json"})
                channeljson = channelrequest.json()['data'][0]
                playsound("WI_ERROR.wav")
                webviewElementEdit("infoText",rf"Duwi is LIVE!!!<br>{channeljson['game_name']}<br>{channeljson['title']}")
                webviewElementEdit("twitch-auth","Click here to join in!","joinDuwi")
            case 'stream.offline':
                webviewElementEdit("infoText","This window will open when Duwi comes online.<br>Minimize it to the tray for now and wait!<br>You can close the app with the X, or from the tray icon.")
                webviewElementEdit('twitch-auth',"Check out Duwi's channel!",'joinDuwi')
            case _:
                pass
        webviewElementEdit("Log",f'Notification received: {notification}')

    def _receiveReconnect(self,payload:dict):
        new_ws_url = payload["session"]["reconnect_url"]
        self._old_websocket = self._current_websocket
        self.start(new_ws_url)

    def _receiveRevocation(self,metadata:dict,payload:dict):
        self.stop()
        window.show()
        webviewElementEdit("infoText","Authentication revoked or expired.<br>Please re-authenticate.")
        webviewElementEdit('twitch-auth','Connect to twitch','connect_button')
        webviewElementEdit("Log", f"Error: {payload["status"]}")