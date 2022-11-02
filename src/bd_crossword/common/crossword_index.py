import textwrap
import sqlite3
from . import index_entry

# def load_index_entry():


class CrosswordIndex:
    def __init__(self, filename=":memory:"):
        self.conn = sqlite3.connect(
            filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        print(filename)
        create_table = textwrap.dedent(
            """CREATE TABLE IF NOT EXISTS index_entry (
                page_date    date,
                title        text,
                url          text,
                hints_author text,
                difficulty   integer,
                enjoyment    integer,
                last_updated timestamp
            )"""
        )
        self.conn.execute(create_table)
        self.conn.row_factory = sqlite3.Row

    def new_index_entry(self, index_entry):
        insert_stmt = textwrap.dedent(
            """INSERT OR REPLACE INTO index_entry
            (page_date, title, url, hints_author, difficulty, enjoyment, last_updated)
            values
            (?, ?, ?, ?, ?, ?, ?)
            """
        )
        self.conn.execute(
            insert_stmt,
            [
                index_entry.page_date,
                index_entry.title,
                index_entry.url,
                index_entry.hints_author,
                index_entry.difficulty,
                index_entry.enjoyment,
                index_entry.last_updated,
            ],
        )
        self.conn.commit()
        self.print_count()

    def retrieve_index_entry_for_date(self, page_date):
        print(f"{page_date=}")

        select_stmt = textwrap.dedent(
            """
            select page_date, title, url,
                hints_author, difficulty, enjoyment, last_updated
            from index_entry
            where page_date = ?
            """
        )
        res = self.conn.execute(select_stmt, [page_date])
        # res = self.conn.execute(select_stmt, [page_date])
        row = res.fetchone()
        if row is not None:
            return index_entry.IndexEntry(
                page_date=row["page_date"],
                title=row["title"],
                url=row["url"],
                hints_author=row["hints_author"],
                difficulty=row["difficulty"],
                enjoyment=row["enjoyment"],
                last_updated=row["last_updated"],
            )
        print("no rows found")
        return None

    def print_count(self):
        print("printing the count")
        select_stmt = "select count(*) from index_entry"
        res = self.conn.execute(select_stmt)
        row = res.fetchone()
        print(row["count(*)"])
