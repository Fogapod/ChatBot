import pycurl, json

STREAM_URL = "https://imv4.vk.com/im2898?act=a_check&key=2522b126a2014fcd5baa251991faf371a57d5a6c&ts=1671810638&version=1"
STREAM_URL = 'https://api.vk.com/method/{}?ts={}&pts={}&fields={}&access_token={}&v={}'.format(\
'messages.getLongPollHistory',
'1671810801',
'1644309',
'sex',
'6cedb48d283f5b33c9e0b1cc7d6257e4612b4e17838ed68ad1927aa64023fc3f518bcdc48db2a359db8ee',
'5.60'
)

class Client:
  def __init__(self):
    self.buffer = ""
    self.conn = pycurl.Curl()
    self.conn.setopt(pycurl.URL, STREAM_URL)
    self.conn.setopt(pycurl.WRITEFUNCTION, self.on_receive)
    self.conn.perform()

  def on_receive(self, data):
    data = data.decode('utf-8')
    try:
      data = json.loads(data)['response']
      print(data)
      print(data['new_pts'])
    except:
      print(data)

client = Client()