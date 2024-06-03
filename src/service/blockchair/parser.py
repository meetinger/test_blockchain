import asyncio

import datetime as dt
from multiprocessing import Process
from pathlib import Path

import httpx


class BlockchairParser:
    def __init__(self, download_dir: str = "downloads") -> None:
        download_dir = Path(download_dir)
        self._download_dir = download_dir
        self._download_dir.mkdir(parents=True, exist_ok=True)

        (download_dir / "transactions").mkdir(parents=True, exist_ok=True)
        (download_dir / "inputs").mkdir(parents=True, exist_ok=True)
        (download_dir / "outputs").mkdir(parents=True, exist_ok=True)
        (download_dir / "addresses").mkdir(parents=True, exist_ok=True)


    async def _download_file(self, url: str) -> bytes:
        response_code = None
        attempts = 0
        async with httpx.AsyncClient() as client:
            while response_code != 200 and attempts < 5:
                attempts += 1
                response = await client.get(url)
                response_code = response.status_code
                print(f"Response code: {response_code}")
            if response_code != 200:
                raise Exception(f"Failed to download file: {url}")
            return response.content

    async def download_transactions(self, date: dt.date) -> bytes:
        url = f"https://gz.blockchair.com/bitcoin/transactions/blockchair_bitcoin_transactions_{date.strftime('%Y%m%d')}.tsv.gz"
        return await self._download_file(url)

    async def download_inputs(self, date: dt.date) -> bytes:
        url = f"https://gz.blockchair.com/bitcoin/inputs/blockchair_bitcoin_inputs_{date.strftime('%Y%m%d')}.tsv.gz"
        return await self._download_file(url)

    async def download_outputs(self, date: dt.date) -> bytes:
        url = f"https://gz.blockchair.com/bitcoin/outputs/blockchair_bitcoin_outputs_{date.strftime('%Y%m%d')}.tsv.gz"
        return await self._download_file(url)

    async def download_addresses(self, date: dt.date) -> bytes:
        url = f"https://gz.blockchair.com/bitcoin/addresses/blockchair_bitcoin_addresses_latest.tsv.gz"
        return await self._download_file(url)

    async def download_all_by_date(self, date: dt.date) -> tuple[bytes, bytes, bytes, bytes]:
        return await asyncio.gather(
            self.download_transactions(date),
            self.download_inputs(date),
            self.download_outputs(date),
            self.download_addresses(date),
        )

    async def download_and_unpack(self, date: dt.date = dt.date.today()):
        transactions, inputs, outputs, addresses = await self.download_all_by_date(date)
        with open(self._download_dir / "transactions" / f"blockchair_bitcoin_transactions_{date.strftime('%Y%m%d')}.tsv", "wb") as f:
            f.write(transactions)
        with open(self._download_dir / "inputs" / f"blockchair_bitcoin_inputs_{date.strftime('%Y%m%d')}.tsv", "wb") as f:
            f.write(inputs)
        with open(self._download_dir / "outputs" / f"blockchair_bitcoin_outputs_{date.strftime('%Y%m%d')}.tsv", "wb") as f:
            f.write(outputs)
        with open(self._download_dir / "addresses" / f"blockchair_bitcoin_addresses_{date.strftime('%Y%m%d')}.tsv", "wb") as f:
            f.write(addresses)

    async def start_downloader_process(self):
        """Запустить процесс для скачивания данных"""
        async def _worker():
            while True:
                dt_now = dt.datetime.now().astimezone(tz=dt.timezone.utc)
                if dt_now.hour == 23 and dt_now.minute == 59 and dt_now.second == 59:
                    await self.download_and_unpack(dt_now.date())
                await asyncio.sleep(30)

        def _worker_wrapper():
            asyncio.run(_worker())

        mp = Process(target=_worker_wrapper)
        mp.start()

        return mp


async def main():
    parser = BlockchairParser()
    await parser.download_and_unpack(date=dt.date(2009, 1, 21))
    # mp = await parser.start_downloader_process()
    # await mp.join()


if __name__ == "__main__":
    asyncio.run(main())