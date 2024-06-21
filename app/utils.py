from app.database import Clan, User, General, Session, Tank, All_General
from app.request import Request_player, Request_clan
import time
import asyncio
from config import LIMITED
from logging import getLogger, FileHandler, Formatter, INFO

logger = getLogger(__name__)
handler = FileHandler(filename=f"log\\{__name__}.log", encoding="utf-8")
handler.setFormatter(
    Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]-%(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )
)
logger.addHandler(handler)
logger.setLevel(INFO)


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(end_time - start_time)
        return result

    return wrapper


class PlayerInterface:
    def __init__(self, name, user_id=None):
        self.name = name
        self.user_id = user_id
        self.player = Request_player(name=name, user_id=self.user_id)
        logger.info("Обработка игрока %s", self.name)

    async def update(self):
        data = await self.player.player_session()
        self.user_id = data["id"]
        old = Session().get(self.user_id)
        if not old:
            Session().add(data=data)
            All_General().add(data=data)
            return "Вас только начали отслеживать"
        else:
            self.time = old.get("data")
            self.old_ses = old.get("all")
            self.now_ses = data["all"]

    async def reset(self):
        data = await self.player.player_session()
        Session().add(data)
        All_General().add(data)

    async def result_of_the_period(self, period: str):
        await self.update()
        self.old_ses = next(
            i["all"] for i in All_General().get(self.name) if i["data"] == period
        )
        self.time = period
        return self.calculate()

    async def results(self):
        res = await self.update()
        if res:
            return res
        return self.calculate()

    def calculate(self):
        result = []
        for i in range(len(self.now_ses)):
            old = None
            tank_id = self.now_ses[i].get("tank_id")
            now = Player_Tank(**self.now_ses[i].get("all"), tank_id=tank_id)
            for j in self.old_ses:
                if j.get("tank_id") == tank_id:
                    old = Player_Tank(**j.get("all"), tank_id=tank_id)
                    break
            if old is None:
                old = Player_Tank(
                    tank_id=tank_id,
                )
            if now.__ne__(old):
                result.append(Stats(old_ses=old, now_ses=now).get_stats())
        if result:
            result.append(Stats.get_general())
            return result
        return "Сыграйте один бой в рандоме"

    async def get_update_tank(self):
        data = await self.get_update_tank_data()
        for dat in data:
            Tank().add(dat)

    def __repr__(self) -> str:
        return f"Игрок {self.name}, id {self.user_id}"


class ClanInterface:
    def __init__(self, name=None, clan_id=None, clan_tag=None):
        self.name = name
        self.clan_id = clan_id
        self.clan_tag = clan_tag
        self.clan = Request_clan(clan_name=name, clan_id=clan_id, clan_tag=clan_tag)
        logger.info(
            "Обработка клана %s", name if name else (clan_tag if clan_tag else clan_id)
        )

    async def update(self):
        data = await self.clan.clan()
        self.clan_id = data["clan_id"]
        self.name = data["name"]
        self.clan_tag = data["tag"]
        old = Clan().get(self.clan_id)
        if not old:
            Clan().add(data=data)
            return "Вас только начали отслеживать"
        else:
            self.time = old.get("data")
            self.old_ses = old.get("players")
            self.now_ses = data["players"]

    async def reset(self):
        data = await self.clan.clan()
        Clan().add(data)

    async def results(self):
        res = await self.update()
        if res:
            return res
        res = []
        for i in range(len(self.now_ses)):
            try:
                old = Player(**self.old_ses[i])
            except:
                old = Player(**self.now_ses[i])
            now = Player(**self.now_ses[i])
            if old.__ne__(now):
                res.append(Stats(old, now).get_stats())
        if res:
            res.append(Stats.get_general())
            return res


class Parameters:
    def __init__(
        self,
        battles=0,
        hits=0,
        shots=0,
        survived_battles=0,
        damage_dealt=0,
        damage_received=0,
        wins=0,
    ):
        self.battles = battles
        self.wins = wins
        self.shots = shots
        self.hits = hits
        self.survival = survived_battles
        self.damage = damage_dealt
        self.damage_received = damage_received


class Player_Tank(Parameters):
    def __init__(self, **kwargs):
        self.tank_id = kwargs.pop("tank_id")
        super().__init__(**kwargs)

    def get_name(self):
        data = Tank().get(tank_id=self.tank_id)
        self.name = data.get("name")
        self.tier = data.get("tier")
        if self.name == "undefined":
            logger.warning(
                "Неопознана машина бои %d победы %d общий урон %d танк_айди %d",
                self.battles,
                self.wins,
                self.damage,
                self.tank_id,
            )
        return self.name, self.tier

    def __eq__(self, other) -> bool:
        if isinstance(other, Player_Tank) and self.tank_id == other.tank_id:
            return self.battles == other.battles
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class Player(Parameters):
    def __init__(self, **kwargs):
        self.name = kwargs.pop("nickname")
        self.id = kwargs.pop("id")
        super().__init__(**kwargs.get("all"))

    def __eq__(self, other) -> bool:
        if isinstance(other, Player) and self.id == other.id:
            return self.battles == other.battles
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return str({"name": self.name, "id": self.id, "battles": self.battles})


class Stats:
    name = "general"
    battles = 0
    wins = 0
    hits = 0
    shots = 0
    survival_battles = 0
    damage_dealt = 0
    damage_received = 0

    def __init__(self, old_ses: Player | Player_Tank, now_ses: Player | Player_Tank):
        if isinstance(now_ses, Player_Tank):
            self.name, self.tier = now_ses.get_name()
        else:
            self.name = now_ses.name
        self.battles = now_ses.battles - old_ses.battles
        self.wins = now_ses.wins - old_ses.wins
        self.shots = now_ses.shots - old_ses.shots
        self.hits = now_ses.hits - old_ses.hits
        self.survival = now_ses.survival - old_ses.survival
        self.damage = now_ses.damage - old_ses.damage
        self.damage_rece = now_ses.damage_received - old_ses.damage_received
        Stats.update(self)

    @classmethod
    def update(cls, self):
        cls.battles += self.battles
        cls.wins += self.wins
        cls.hits += self.hits
        cls.shots += self.shots
        cls.survival_battles += self.survival
        cls.damage_dealt += self.damage
        cls.damage_received += self.damage_rece

    @classmethod
    def get_general(cls):
        data = {
            "Имя": cls.name,
            "Бои": cls.battles,
            "Победы": round(cls.wins / cls.battles * 100, 2),
            "Средний урон": round(cls.damage_dealt / cls.battles, 2),
            "Точность": 0 if cls.shots == 0 else round(cls.hits / cls.shots * 100, 2),
            "Выживаемость": round(cls.survival_battles / cls.battles * 100, 2),
            "КПД": (
                0
                if cls.damage_received == 0
                else round(cls.damage_dealt / cls.damage_received, 2)
            ),
        }
        cls.restart()
        return data

    @classmethod
    def restart(cls):
        cls.battles = 0
        cls.wins = 0
        cls.hits = 0
        cls.shots = 0
        cls.survival_battles = 0
        cls.damage_dealt = 0
        cls.damage_rece = 0

    def get_stats(self):
        if hasattr(self, "tier"):
            stats = {
                "Имя": self.name,
                "Уровень": self.tier,
                "Бои": self.battles,
                "Победы": round(self.wins / self.battles * 100, 2),
                "Средний урон": round(self.damage / self.battles, 2),
                "Точность": (
                    0 if self.shots == 0 else round(self.hits / self.shots * 100, 2)
                ),
                "Выживаемость": round(self.survival / self.battles * 100, 2),
                "КПД": (
                    0
                    if self.damage_rece == 0
                    else round(self.damage / self.damage_rece, 2)
                ),
            }
        else:
            stats = {
                "Имя": self.name,
                "Бои": self.battles,
                "Победы": round(self.wins / self.battles * 100, 2),
                "Средний урон": round(self.damage / self.battles, 2),
                "Точность": (
                    0 if self.shots == 0 else round(self.hits / self.shots * 100, 2)
                ),
                "Выживаемость": round(self.survival / self.battles * 100, 2),
                "КПД": (
                    0
                    if self.damage_rece == 0
                    else round(self.damage / self.damage_rece, 2)
                ),
            }
        return stats


class Container_class:
    def __init__(self):
        self.players: list[PlayerInterface] = []
        self.clans: list[ClanInterface] = []
        self.task = []
        self.total_task = 0
        self.completed_tasks = 0
        self.semaphore = asyncio.Semaphore(LIMITED)

    def add(self, other):
        if isinstance(other, PlayerInterface):
            self.players.append(other)
        elif isinstance(other, ClanInterface):
            self.clans.append(other)
        else:
            return False

    def update(self):
        asyncio.run(self.update_clan())
        asyncio.run(self.update_player())

    async def update_clan(self):
        for clan in self.clans:
            self.total_task += 1
            self.task.append(clan.reset())
        await self.run_task()

    async def update_player(self):
        for player in self.players:
            self.total_task += 1
            self.task.append(player.reset())
        await self.run_task()

    async def run_task(self):
        async def run(сoruntina):
            async with self.semaphore:
                await сoruntina
                self.completed_tasks += 1

        await asyncio.gather(*[run(task) for task in self.task])

    def get_clan(
        self,
    ):
        self.clans.clear()
        for item in Clan().get_all_id():
            self.add(ClanInterface(clan_id=item.get("clan_id")))

    def get_player(
        self,
    ):
        self.players.clear()
        for item in Session().get_all_id():
            self.add(PlayerInterface(user_id=item.get("id"), name=item.get("nickname")))

    def __str__(self):
        return str(self.players)


def main(): ...
