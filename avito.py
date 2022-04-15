import json,time,re,asyncio,random,array

import requests

from aiogram import types
from aiogram.utils.exceptions import MessageTextIsEmpty

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException


class Avito():
    def __init__(self,config):
        self.items=array.array('l')
        self.search_words=config.tg_bot.search_words
        self.stop_words=config.tg_bot.stop_words
        self.driver_path=config.tg_bot.driver_path

    async def close_browser(self):
        self.browser.close()
        self.browser.quit()
        await self.start_browser()

    async def start_browser(self):
        service = Service(executable_path=self.driver_path)
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("--headless")
        self.browser=webdriver.Chrome(options=options,service=service)
        print('Запуск браузера')
        self.browser.set_page_load_timeout(20)
        self.browser.delete_all_cookies()
        await self.message.answer("Парсинг запущен ✅")
        try:
            self.browser.get('https://www.avito.ru/')
            time.sleep(3)
            self.browser.refresh()
            while True:
                t1=time.time()
                try:
                    self.browser.get('https://www.avito.ru/api/11/items?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir&categoryId=97&params[137]=613&locationId=621540&localPriority=1&sort=date&isGeoProps=true&presentationType=serp&priceMin={}&limit=5'.format(str(random.randint(4000,4100))))
                    self.jsonObj=json.loads(self.browser.find_element_by_xpath('/html/body/pre').text)
                except:
                    print("Exit from loop")
                    await self.close_browser()
                if 'code' in self.jsonObj and self.jsonObj['code'] == 403:
                    print(self.jsonObj['error']['message'])
                    break
                else:
                    asyncio.ensure_future(self.parse())
                    await asyncio.sleep(1)
                    t2=time.time()
                    print("{:.2f}".format(t2-t1))
        except:
            print('Exit from start_browser()')
            await self.close_browser()
        finally:
            print("finally")
            await self.close_browser()

    async def parse(self):
        try:
            for id in (item['value']['id'] for item in self.jsonObj['result']['items'] if item['type'] != 'snippet'
                       if re.findall(self.search_words,item['value']['uri_mweb'])
                       and not re.findall(self.stop_words,item['value']['uri_mweb'])
                       if item['value']['id'] not in self.items):
                self.items.append(int(id))
                await self.get_content(id)
        except KeyError:
            pass

    async def get_content(self,id):
        self.browser.execute_script('''window.open();''')
        self.browser.switch_to.window(self.browser.window_handles[1])
        try:
            self.browser.get("https://www.avito.ru/api/15/items/{}?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir".format(str(id)))
            jsonObj2=json.loads(self.browser.find_element_by_xpath('/html/body/pre').text)
            if 'code' in jsonObj2 and jsonObj2['code'] == 403:self.browser.close()
            elif jsonObj2['firebaseParams']['isShop'] == 1:self.browser.close()
            else:
                await self.message.answer(f"{jsonObj2['title']} \
                    \n\n Цена 💵 : {jsonObj2['price']['value']} \n \
                    \n 📌 Расположение: {jsonObj2['address']} \
                    \n {jsonObj2['sharing']['url']} \
                    \n\n Описание: \n {jsonObj2['description']}")
                    # \n\n{jsonObj2['images'][0]['240x180']}")
                self.browser.close()
        except:
            self.browser.close()
        finally:
            self.browser.switch_to.window(self.browser.window_handles[0])

    async def get_phone(self,id):
        headers={
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            }

        cookie="""st=t%3AeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoidko0TkJ5SlU2TElJTGRDY3VNTkdBZm5PRWwySzdtS01KZXBFMDh1VUFIS2FCTlI0em5rRWNvb0x1S1ZJZW1DNllhQkN5Vi9BclR5Qk0xSGdObTZsTzRNbmx4bTZSVWJ3aGR2UndBZ2xYUTkwVlNXVTQrMXNFRFUzZEFWRFVrWlp6ckJQaUVYRUZFZDdZREVBbGRFbDhZZms1dnFxZzZzeHo0Nk50Y05kWVdtYlVFQnZ1azA1Z1kyZUxCN1I5amx4UG0yUm5jREh3YjRQbWFWZE5vZE9WTTF4eE1tam5CWHQ1ei82ZUdNTDdVenJSRmZZK1ZUbUdNUG5nRFIxT0cxamdtV1B2QmJ2Q0dldVptYmRRdlh6VkRTMGdqb2drQlE2WjdaMFB2bnUvMmF6cDNEME1ycDlFMGh1Ym9pZllLUXZSNmNhREhqZngxSnFRckt1OGhIQkZtcXB0TW1uNHROS1ErSThnTkI2L3UyY1huN0ZkOUpNQVRjTGRlU2pITmtlbXBOQ2lIejVTVXRHZitqZCtHb3haQ0lxVjhFaW1FMFV1SHBPYlV0WnU5ZWRsdnBhMnBkNnVYdTlBVE5RTjNQdytSZ1lzbUhRVm9Ob0NhdDhub0J4a3ZTMkMxR1MvWE41MHZmbjFUcitwMWlHWTFXaUFPNWRHajFXZ2dkb3JFZ1NUV2tMd3VHWE5hOHNqbFQ4L0RlNjRKTVN3N3gxYVYwNnJ0MnFxaE8xY1U3UzBhYnJyUll5dHRCWU1SN3RldnVoNm1yWVhFclRoWS9ITGRlajJSaFhtTENnaE1qWU1IbWtSZVNlNEIySk9uSVZkbmxzR3RBOVlYTmFxVUtHYlQrVDhvK0VMb3I1VjArSmpGYUxISnI1OG84SmhGNzhpRXM5K2JGR1VVVTRqWlROejlrT3BEb2hqYVFlUGVUTExyYkdhTWo4Yk1la3lCdWxlSTV3VjNOaUdLMUxXeUVGRlg5bjBlOHF3UWdyK0RzTXJGYWh0NzBmSUsvTmNPUEJkZUQ2QSt3c25PbHNLUnRWNXIvVS8zK2JLb1JRemVpRGZsa1FOS1ZiTGk1Wjk5eXVNeE1mT09ENlplY3RybG11VmY4cVNIMWNlT1JwL0pRb0FVUWw4TmYrSFRLSUt1Um9BQUd2NG1rNlFxbzUwMmU1MVoyaW5lL3ZNa2tYS000NWtMaDQ3RGpqbUVaWnpUcFIyV0hwSVdmb0VRPT0iLCJpYXQiOjE2NDIyODg2OTYsImV4cCI6MTY0MzQ5ODI5Nn0.kzXLRDQOHqSzTPJ_hM8FbZ-FWjHR-zN2k4Lsm5nWT1w%26e%3AsYIe4KWWFvRjfkOvZ%2B9jsVzcb5HZvxwF1wGncxB0QUZZXs1TObOTUQQMadRFHn1iJgZ1yXkQlnaTc1OHLxuTKW%2BY2z%2BWRIyp6CHrsQ5zskmifv59%2F%2FpCitOW6AKqlltmvX04xVGc4w%2BnNBjseyzwvpao8N7lkdetiqXF6q%2BqYBaiOvpGY46q0tYBgKLGB%2BdDleIKKR1t1lfMYmQpUwftCARXbOVRSDRd2Mg1yxpbKOdvDRdGhHYgUd%2FZ3B2ky6Nx6TyFssWTAGjxNepq1Ufe45IaENoGNUInTb8QMFZf0xi%2FLPoK2ddzqIV4zC7Ro4Qg1T5NGnHgbbzJLGBGF6qDEg%3D%3D.WwlAjltlHSf1CI8X; v=1642288673; sx=H4sIAAAAAAACA4uOBQApu0wNAgAAAA%3D%3D; u=2t4axbt5.1dnu37p.1lbo42lyv2f00; dfp_group=22; luri=moskva; sessid=ca1249a66c393f7fd486b6035fe17004.1642288850; _mlocation=621540; _mlocation_mode=laas; ft="zwTs5UmmWIhiW0kp+jbval0JO0vlLSpRuLsUGdePNbYIBhibn2xap4VkT0jJUhqqFNNW7svuFJbQVzRvVk71jr9zWsCix8nNTERJXybQcBuG9yxDg9kUwrbEa9siteUM/6aBEyDVS/O6crVHgnfTFGy96hdZGwxmXKh++M9nsG0aOppGo1HplylGu1fGmcG8"; f=5.88881e344776caaa4b5abdd419952845a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e94f9572e6986d0c624f9572e6986d0c624f9572e6986d0c62ba029cd346349f36c1e8912fd5a48d02c1e8912fd5a48d0246b8ae4e81acb9fa143114829cf33ca746b8ae4e81acb9fad99271d186dc1cd062a5120551ae78ed10ccd2dbdc93417848bdd0f4e425aba7085d5b6a45ae867377bdb88c79240d0191e52da22a560f550df103df0c26013a2ebf3cb6fd35a0ac71e7cb57bbcb8e0ff0c77052689da50ddc5322845a0cba1aba0ac8037e2b74f92da10fb74cac1eab2da10fb74cac1eab2da10fb74cac1eabdc5322845a0cba1a0df103df0c26013a1d6703cbe432bc2a40676b2c2e13de853fa73c465de2edb56243e24ac8c24c876c6bf7e60fb31a89206f21b04059ac992c64d38d813bca5c548f1d7586e524a98ae805666d66480ab6d4055c8a6886742da10fb74cac1eab0df103df0c26013a0df103df0c26013aafbc9dcfc006bed98b1f7e717680fa909e390ce618e2ba853de19da9ed218fe23de19da9ed218fe28e875143a88a6a55d76ae8c8fc09dfb045c84e13b99a7302; lastViewingTime=1642288675145; showedStoryIds=87-86-85-84-83-82-81-79-78-77-76-75-74-71-69-68-61-59"""

        headers['Cookie'] = cookie
        self.ls.headers.update(headers)

        jsonObj3=self.ls.get('https://m.avito.ru/api/1/items/{}/phone?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir'.format(id)).json()
        if jsonObj3['status'] == 'ok':
            try:
                phone=requests.utils.unquote(jsonObj3['result']['action']['uri'].split('number=')[1])
                return (f"☎️ {phone}")
            except IndexError as e:
                print(e)
        #Лимит номеров
        elif jsonObj3['status'] == 'failure' and jsonObj3['result']['error'] == 'exceeded_limit':
            return jsonObj3['result']['error']
            #смена логина:пароля
        #Аутентификация
        elif jsonObj3['status'] == 'failure': # need_confirmed_phone
            return jsonObj3['result']['error']
        #Номер не доступен
        elif jsonObj3['status'] == 'bad-request':
            return (jsonObj3['result']['message'])


def main():
    pass
if __name__ == "__main__":
    main()
