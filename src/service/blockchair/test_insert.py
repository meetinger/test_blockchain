import asyncio
import datetime as dt

from core.log import main_logger
from src.service.blockchair.parser import blockchair_parser


async def main():
    main_logger.info("Start test insertion...")

    inputs_df, outputs_df = blockchair_parser.parse_data_to_df(dt.date(2024, 6, 6))
    await blockchair_parser.insert_data_to_db(inputs_df, outputs_df, break_limit=20000)

    main_logger.info("Test insertion done. Enjoy!")

if __name__ == "__main__":
    asyncio.run(main())
