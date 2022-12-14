import requests, websocket, ssl
from base64 import b64encode

r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/ServiceLookup",
    cert=(".pxgrid-client.crt",".pxgrid-client.key"),
    verify=".demo-ca.cer",
    auth=("pxgrid-client","none"),
    json={
        "name": "com.cisco.ise.session"
    }
)
r.raise_for_status()
service_info=r.json()["services"][0]
session_topic=service_info["properties"]["sessionTopic"]
pubsub_service=service_info["properties"]["wsPubsubService"]
r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/ServiceLookup",
    cert=(".pxgrid-client.crt",".pxgrid-client.key"),
    verify=".demo-ca.cer",
    auth=("pxgrid-client","none"),
    json={
        "name": pubsub_service
    }
)
r.raise_for_status()
service_info=r.json()["services"][0]
node_name=service_info["nodeName"]
ws_url=service_info["properties"]["wsUrl"]
r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/AccessSecret",
    cert=(".pxgrid-client.crt",".pxgrid-client.key"),
    verify=".demo-ca.cer",
    auth=("pxgrid-client","none"),
    json={
        "peerNodeName": node_name
    }
)
r.raise_for_status()
secret=r.json()["secret"]

def on_open(wsapp):
    wsapp.send(f"CONNECT\naccept-version:1.2\nhost:{node_name}\n\n\x00",websocket.ABNF.OPCODE_BINARY)
    wsapp.send(f"SUBSCRIBE\ndestination:{session_topic}\nid:python\n\n\x00",websocket.ABNF.OPCODE_BINARY)

def on_message(wsapp,message):
    print(message.decode())

ssl_context=ssl.create_default_context()
ssl_context.load_verify_locations(cafile=".demo-ca.cer")
wsapp=websocket.WebSocketApp(ws_url,
    on_message=on_message,
    on_open=on_open,
    header={"Authorization": "Basic "+b64encode((f"pxgrid-client:{secret}").encode()).decode()}
)
wsapp.run_forever(sslopt={"context": ssl_context})