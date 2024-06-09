import asyncio
import gzip
import datetime as dt
import io

from multiprocessing import Process
from pathlib import Path

import httpx
import pandas as pd

from core.log import main_logger
from core.settings import settings
from db.neo4j_models.models import Address, Transaction


class BlockchairParser:
    def __init__(self, download_dir: str = "downloads", blockchair_api_key: str = None) -> None:
        download_dir = Path(download_dir)
        self._download_dir = download_dir
        self._download_dir.mkdir(parents=True, exist_ok=True)
        self._blockchair_api_key = blockchair_api_key
        self._process = None

        (download_dir / "transactions").mkdir(parents=True, exist_ok=True)
        (download_dir / "inputs").mkdir(parents=True, exist_ok=True)
        (download_dir / "outputs").mkdir(parents=True, exist_ok=True)
        (download_dir / "addresses").mkdir(parents=True, exist_ok=True)

    async def _download_file(self, url: str, file: io.BytesIO = io.BytesIO()) -> io.BytesIO:
        response_code = None
        attempts = 0
        headers = {}
        if self._blockchair_api_key is not None:
            url = f"{url}?key={self._blockchair_api_key}"
            main_logger.info(url)

        async with httpx.AsyncClient() as client:
            while response_code != 200 and attempts < 5:
                attempts += 1
                response = await client.get(url, headers=headers)
                response_code = response.status_code
                main_logger.info(f"Response code: {response_code}")
            if response_code != 200:
                raise Exception(f"Failed to download file: {url}")
            file.write(response.content)
            return file

    async def download_transactions(self, date: dt.date) -> io.BytesIO:
        url = f"https://gz.blockchair.com/bitcoin/transactions/blockchair_bitcoin_transactions_{date.strftime('%Y%m%d')}.tsv.gz"
        return await self._download_file(url)

    async def download_inputs(self, date: dt.date) -> io.BytesIO:
        url = f"https://gz.blockchair.com/bitcoin/inputs/blockchair_bitcoin_inputs_{date.strftime('%Y%m%d')}.tsv.gz"
        return await self._download_file(url)

    async def download_outputs(self, date: dt.date) -> io.BytesIO:
        url = f"https://gz.blockchair.com/bitcoin/outputs/blockchair_bitcoin_outputs_{date.strftime('%Y%m%d')}.tsv.gz"
        return await self._download_file(url)

    async def download_addresses(self, date: dt.date) -> io.BytesIO:
        url = f"https://gz.blockchair.com/bitcoin/addresses/blockchair_bitcoin_addresses_latest.tsv.gz"
        return await self._download_file(url)

    async def download_all_by_date(self, date: dt.date) -> tuple[io.BytesIO, io.BytesIO, io.BytesIO, io.BytesIO]:
        return await asyncio.gather(
            self.download_transactions(date),
            self.download_inputs(date),
            self.download_outputs(date),
            self.download_addresses(date),
        )

    async def download_and_unpack(self, date: dt.date = dt.date.today()):
        # у blockchair есть ограничение, поэтому от асинхронной загрузки нет толку
        # transactions, inputs, outputs, addresses = await self.download_all_by_date(date)

        main_logger.info(f"Downloading data for {date}...")

        main_logger.info("Downloading transactions...")
        transactions = await self.download_transactions(date)
        transactions.seek(0)

        main_logger.info("Transactions downloaded")
        main_logger.info("Unpacking transactions...")
        with (gzip.open(transactions) as gzip_file,
              open(self._download_dir /
                   "transactions" /
                   f"blockchair_bitcoin_transactions_{date.strftime('%Y%m%d')}.tsv", "wb") as f):
            f.write(gzip_file.read())

        main_logger.info("Unpacking transactions done")

        main_logger.info("Downloading inputs...")
        inputs = await self.download_inputs(date)
        inputs.seek(0)
        main_logger.info("Inputs downloaded")
        main_logger.info("Unpacking inputs...")

        with (gzip.open(inputs) as gzip_file,
              open(self._download_dir / "inputs" / f"blockchair_bitcoin_inputs_{date.strftime('%Y%m%d')}.tsv",
                   "wb") as f):
            f.write(gzip_file.read())

        main_logger.info("Unpacking inputs done")

        main_logger.info("Downloading outputs...")

        outputs = await self.download_outputs(date)
        outputs.seek(0)

        main_logger.info("Outputs downloaded")
        with (gzip.open(outputs) as gzip_file,
              open(self._download_dir / "outputs" / f"blockchair_bitcoin_outputs_{date.strftime('%Y%m%d')}.tsv",
                   "wb") as f):
            f.write(gzip_file.read())

        main_logger.info("Unpacking outputs done")

    async def download_and_insert_to_db(self, date: dt.date):
        main_logger.info(f"Downloading data for {date}")
        await self.download_and_unpack(date)
        main_logger.info(f"Data for {date} downloaded")
        main_logger.info("Inserting data to db...")
        await self.insert_data_to_db(*self.parse_data_to_df(date))
        main_logger.info("Data inserted to db")

    def stop_downloader_process(self):
        """Остановить процесс для скачивания данных"""
        if self._process is not None:
            self._process.terminate()

    def force_download_and_insert_to_db(self):
        self.stop_downloader_process()

        main_logger.info("Force download and insert to db...")

        date = dt.datetime.now().astimezone(tz=dt.timezone.utc).date()
        async def _worker():
            await self.download_and_insert_to_db(date)

        def _worker_wrapper():
            asyncio.run(_worker())

        self._process = Process(target=_worker_wrapper)
        self._process.start()
        self._process.join()

        main_logger.info("Force download and insert to db done")
        main_logger.info("Start blockchair downloader process...")

        self.start_downloader_process()

        return self._process

    def start_downloader_process(self):
        """Запустить процесс для скачивания данных"""
        self.stop_downloader_process()

        main_logger.info("Start blockchair downloader")

        async def _worker():
            dt_now_last = dt.datetime.now().astimezone(tz=dt.timezone.utc)
            while True:
                dt_now = dt.datetime.now().astimezone(tz=dt.timezone.utc)
                main_logger.info("Checking for new day...")
                if dt_now_last.day != dt_now.day:
                    await self.download_and_insert_to_db(dt_now.date())
                else:
                    main_logger.info("No new day, sleeping...")
                dt_now_last = dt_now
                await asyncio.sleep(60)

        def _worker_wrapper():
            asyncio.run(_worker())

        self._process = Process(target=_worker_wrapper)
        self._process.start()

        return self._process

    def parse_data_to_df(self, date: dt.date):
        inputs = pd.read_csv(self._download_dir / "inputs" / f"blockchair_bitcoin_inputs_{date.strftime('%Y%m%d')}.tsv", sep="\t")
        outputs = pd.read_csv(self._download_dir / "outputs" / f"blockchair_bitcoin_outputs_{date.strftime('%Y%m%d')}.tsv", sep="\t")
        # transactions = pd.read_csv(self._download_dir / "transactions" / f"blockchair_bitcoin_transactions_{date.strftime('%Y%m%d')}.tsv", sep="\t")
        return inputs, outputs

    @classmethod
    async def insert_data_to_db(cls, inputs_df: pd.DataFrame, outputs_df: pd.DataFrame, break_limit: int=10000):
        """
        Метод загрузки данных в базу данных.
        Это можно оптимизировать, используя различные операции с pandas и asyncio
        Также можно загружать данные батчами и тд.
        """

        main_logger.info("Inserting data to db...")

        all_recipients = pd.concat([inputs_df['recipient'], outputs_df['recipient']]).unique()

        main_logger.info(f"Creating addresses for {len(all_recipients)} recipients...")

        address_values = [{'address': recipient} for recipient in all_recipients]

        main_logger.info("Fetching or creating addresses...")
        addresses = []
        for i in range(0, len(address_values), 100):
            if break_limit and i > break_limit:
                break
            main_logger.info(f"Fetching or creating addresses from {i} to {i + 100}...")
            addresses.extend(await Address.get_or_create(*address_values[i:i + 100], columns=['address']))

        address_dict = {address.address: address for address in addresses}

        for idx, (_, i_row) in enumerate(inputs_df.iterrows()):
            addr = address_dict.get(i_row['recipient'])
            if addr:
                tx = await Transaction.nodes.get_or_none(transaction_hash=i_row['transaction_hash'])
                if not tx:
                    tx = Transaction(
                        transaction_hash=i_row['transaction_hash'],
                        value=i_row['value'],
                        block_id=i_row['block_id'],
                        time=i_row['time']
                    )
                    await tx.save()

                await tx.inputs.connect(addr)
            if idx % 500 == 0:
                main_logger.info(f"Inputs processed: {idx} of {len(inputs_df)}")
            if break_limit and idx > break_limit:
                break

        for idx, (_, o_row) in enumerate(outputs_df.iterrows()):
            addr = address_dict.get(o_row['recipient'])
            if addr:
                tx = await Transaction.nodes.get_or_none(transaction_hash=o_row['transaction_hash'])
                if not tx:
                    tx = Transaction(
                        transaction_hash=o_row['transaction_hash'],
                        value=o_row['value'],
                        block_id=o_row['block_id'],
                        time=o_row['time']
                    )
                    await tx.save()

                await tx.outputs.connect(addr)
            if idx % 500 == 0:
                main_logger.info(f"Outputs processed: {idx} of {len(outputs_df)}")
            if break_limit and idx > break_limit:
                break


blockchair_parser = BlockchairParser(download_dir=settings.BLOCKCHAIR_DOWNLOADS_DIR)
