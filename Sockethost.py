from webhost import validateToken, webviewElementEdit, window
from websockets.sync.client import connect,ClientConnection
from json import loads
from threading import Timer,Lock
import requests

APP_TIMEOUT = 600  #INT between 10 and 600
APP_CLIENT_ID = "5wzg88m34ulgtxj4fdfazf9d2mpxq1"
WS_URL = f'wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds={APP_TIMEOUT}'
EVENT_SUB_URL = "https://api.twitch.tv/helix/eventsub/subscriptions"
DUWI_ID = '463761283'

class liveListener():
    def __init__(self):
        self.accesstoken = None
        self._current_websocket = None
        self._old_websocket: ClientConnection = None
        self._watchdog = None
        self._watchdog_lock = Lock()

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
        print('Timed out')
        self.start()

    def start(self,URL:str = WS_URL,accesstoken:str = None):
        if accesstoken:
            self.accesstoken = accesstoken
        try:
            with connect(URL) as ws:
                self._current_websocket = ws
                validationcycle = 0 #Token must be validated every hour.
                while True:
                    validationcycle += 1
                    if validationcycle >= 6:
                        validationcycle = 0
                        if not validateToken(self.accesstoken):
                            self.stop()
                            window.show()
                            webviewElementEdit("infoText","Authentication revoked or expired.<br>Please re-authenticate.")
                            webviewElementEdit('twitch-auth','Connect to twitch','connect_button')
                            break
                    message = loads(ws.recv())
                    self._handleMessage(message)
        except Exception as e:
            #TODO Implement an error message system
            print(f'Error - {e} - {e.args}')

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
                print('Keep alive')
            case "session_reconnect":
                self._receiveReconnect(payload)
            case "revocation":
                self._receiveRevocation(metadata,payload)
            case _:
                print(f'Unknown message - {message}')
    
    def _requestSubscription(self,sessionid:str,accesstoken:str):
        headers = {
            "Authorization": f"Bearer {accesstoken}",
            "Client-Id": APP_CLIENT_ID,
            "Content-Type": "application/json"
            }
        body = {
            "type": "stream.online",
            "version": "1",
            "condition": {
                "broadcaster_user_id": DUWI_ID
            },
            "transport": {
                "method": "websocket",
                "session_id": sessionid
            }
        }
        sub = requests.post(EVENT_SUB_URL,headers=headers,json=body)
        print(sub.status_code)

    def _receiveNotification(self,metadata:dict,payload:dict):
        window.show()
        webviewElementEdit("infoText","Duwi is LIVE!!!")# Add timestamp - <br>Started at ...
        webviewElementEdit("twitch-auth","Click here to join in!","joinDuwi")
        notification = payload["event"]
        print(notification)

    def _receiveReconnect(self,payload:dict):
        new_ws_url = payload["session"]["reconnect_url"]
        print(f"Reconnecting at {new_ws_url}")
        self._old_websocket = self._current_websocket
        self.start(new_ws_url)

    def _receiveRevocation(self,metadata:dict,payload:dict):
        self._current_websocket.close()
        webviewElementEdit("infoText","Authentication revoked or expired.<br>Please re-authenticate.")
        webviewElementEdit('twitch-auth','Connect to twitch','connect_button')
        print(payload)