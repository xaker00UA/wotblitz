import asyncio
from aiohttp import ClientSession, TCPConnector
from asyncio import Semaphore, Queue
from datetime import datetime
from config import LIMITED, APPLICATION_ID
from Error.error_name import ConnectionError, Not_Found_Player


async def fetch(session: ClientSession, url, param, semaphore: Semaphore):
    async with semaphore:
        async with session.get(url, params=param) as response:
            data = await response.json()
            if data.get("status") == "error":
                raise ConnectionError("Ошибка соединения", data)
            if data.get("meta").get("count") == 0:
                raise Not_Found_Player(f"Пользователь {param.get('search')} не найден")
            return await response.json()


async def task(url, params):
    sem = Semaphore(LIMITED)
    async with ClientSession() as session:
        tasks = [
            asyncio.create_task(
                fetch(session=session, url=url, param=par, semaphore=sem)
            )
            for par in params
        ]
        return await asyncio.gather(*tasks)


class Get_url:
    def __init__(self):
        self.__application_id = APPLICATION_ID

    def get_general_session(self, user_id) -> set:
        return "https://api.wotblitz.eu/wotb/account/info/", {
            "account_id": user_id,
            "application_id": self.__application_id,
            "fields": "statistics.all.hits, statistics.all.wins, statistics.all.battles, statistics.all.shots,"
            "statistics.all.survived_battles, statistics.all.damage_dealt, statistics.all.damage_received, nickname",
        }

    def get_tank(self) -> set:
        return "https://api.wotblitz.eu/wotb/encyclopedia/vehicles/", {
            "fields": "name, tier, tank_id",
            "application_id": self.__application_id,
        }

    def get_session(self, user_id) -> set:
        return "https://api.wotblitz.eu/wotb/tanks/stats/", {
            "account_id": user_id,
            "fields": "all.hits, all.wins, all.battles, all.shots, all.survived_battles, all.damage_dealt, all.damage_received, tank_id",
            "application_id": self.__application_id,
        }

    def get_account_id(self, name) -> set:
        return "https://api.wotblitz.eu/wotb/account/list/", {
            "application_id": self.__application_id,
            "search": name,
            "type": "exact",
        }

    def get_clan_id(self, clan_name) -> set:
        return "https://api.wotblitz.eu/wotb/clans/list/", {
            "application_id": self.__application_id,
            "fields": "clan_id, name, tag",
            "search": clan_name,
        }

    def clan_members(self, clan_id) -> set:
        return "https://api.wotblitz.eu/wotb/clans/info/", {
            "application_id": self.__application_id,
            "clan_id": clan_id,
        }


class Request_player:
    def __init__(self, name=None, user_id=None):
        self.__name: str = name
        self.__user_id: int = user_id
        self.date = Get_url()

    async def __get_user_id(self):
        api, params = self.date.get_account_id(self.__name)
        data = await task(url=api, params=[params])
        self.__user_id = data[0].get("data")[0].get("account_id")

    async def player_session(self) -> list[dict]:
        if not self.__user_id:
            await self.__get_user_id()
        api, params = self.date.get_session(self.__user_id)
        data = await task(url=api, params=[params])
        return {
            "nickname": self.__name,
            "id": self.__user_id,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "all": data[0].get("data").get(str(self.__user_id)),
        }

    async def player_general_session(self, user_id) -> list[dict]:
        api, params = self.date.get_general_session(user_id=user_id)
        data = await task(url=api, params=[params])
        data = data[0].get("data").get(str(user_id))
        return user_id, data.get("nickname"), data["statistics"].get("all")

    async def get_update_tank(self):
        api, par = self.date.get_tank()
        data = asyncio.run(task(url=api, params=[par]))
        return data[0].get("data").values()


class Request_clan:
    def __init__(
        self,
        clan_name=None,
        clan_id=None,
        clan_tag=None,
    ):
        self.__clan_id: int = clan_id
        self.__clan_name: str = clan_name
        self.__clan_tag: str = clan_tag
        self.date = Get_url()

    async def __get_clan_id(self):
        api, params = self.date.get_clan_id(
            self.__clan_name if self.__clan_name else self.__clan_tag
        )
        data = await task(url=api, params=[params])
        for clan in data[0].get("data"):
            if self.__clan_name.upper() == clan.get(
                "tag"
            ) or self.__clan_name == clan.get("name"):
                self.__clan_id = clan.get("clan_id")
                self.__clan_tag = clan.get("tag")
                self.__clan_name = clan.get("name")
                break

    async def clan(self):
        items = await self.__clan_members()
        params = []
        for item in items:
            api, par = self.date.get_general_session(user_id=item)
            params.append(par)
        data = await task(url=api, params=params)
        res = []
        for item in data:
            acc_id = list(item["data"].keys())[0]
            nick = item["data"][acc_id]["nickname"]
            all = item["data"][acc_id]["statistics"]["all"]
            res.append({"nickname": nick, "id": int(acc_id), "all": all})
        return {
            "tag": self.__clan_tag,
            "name": self.__clan_name,
            "clan_id": self.__clan_id,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "players": res,
        }

    async def __clan_members(self) -> list[int]:
        if not self.__clan_id:
            await self.__get_clan_id()
        api, params = self.date.clan_members(self.__clan_id)
        data = await task(url=api, params=[params])
        self.__clan_name, self.__clan_tag = (
            data[0]["data"][str(self.__clan_id)]["tag"],
            data[0]["data"][str(self.__clan_id)]["name"],
        )
        return data[0].get("data").get(str(self.__clan_id)).get("members_ids")
